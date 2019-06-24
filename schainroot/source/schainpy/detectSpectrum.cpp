/*
@Author: Alejandro Castro
Created: June, 2019
*/
#include <Python.h>
#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <cfloat>
using namespace std;


static int GetMaxIndex(double* spec2_tmp, int size){
	double max = spec2_tmp[0];
	int ind = 0;

	double value;
	for (int i=0;i< size; i++){
		value = spec2_tmp[i];
		if (value>max){
			max=value;
			ind = i;
		}
	}
	return ind;
}


static void GetFirstLesserInRange(double* spec2_tmp, int start, int end, double threshold,
	vector<int> &result){

	//Resetting the vector to send a new vector;
	result.clear();
	vector<int>().swap(result);

	for (int i=start; i< end; i++){
		if (spec2_tmp[i]< threshold) {
			result.push_back(i);
		}
	}
}

static double GetSumInRange(PyObject *array, int start, int end){
	double result=0;
	for(int i=start; i<end; i++){
		result = result + PyFloat_AsDouble(PyList_GetItem(array, i));
	}
	return result;
}

vector<double> CalcMomentValues(int ss1, int bb0, PyObject* spec2_obj, PyObject* freq_obj, double n0, bool powerf=true,
	bool dopplerf=true, bool wf=true){

	double aux_value;
	double *spec2_tmp = (double*)malloc(sizeof(double)*(bb0+1-ss1));
	vector<double> result;

	for(int i=ss1; i< (bb0+1);i++){
		aux_value= PyFloat_AsDouble(PyList_GetItem(spec2_obj, i));
		if (aux_value < n0)	aux_value = min(1e-20, aux_value);
		else aux_value = aux_value  - n0;
		spec2_tmp[i-ss1] = aux_value;
	}

	double power= 0.0;
	if (powerf){
		for (int i=ss1; i<(bb0+1);i++){
			power = power + spec2_tmp[i-ss1]; //m_0 = first moments
		}
	}


	// TODO probar la estimacion de fd con el calculo de ruido por perfil.

	double fd = 0.0;
	if (dopplerf){
		for (int i=ss1; i<(bb0+1);i++){
			fd = fd + spec2_tmp[i-ss1]*PyFloat_AsDouble(PyList_GetItem(freq_obj, i)) ;
		}
		fd = fd / power;//doppler frequency
	}

	double w = 0.0;
	if (wf){
		for (int i=ss1; i<(bb0+1);i++){
			w = w + spec2_tmp[i-ss1]*pow(PyFloat_AsDouble(PyList_GetItem(freq_obj, i)) - fd, 2);
		}
		w = sqrt(w / power);//spectral width
	}
	free(spec2_tmp);

	result.push_back(power), result.push_back(fd), result.push_back(w);
	return result;
}


static PyObject *DetectSpectrumInSpectrogram(PyObject *self, PyObject *args){
	// The first three parameters should be PyObjects only because we wanted to modified them
	PyObject *vec_power_obj = NULL, *vec_fd_obj = NULL, *vec_w_obj = NULL, *vec_snr_obj=NULL, *freq_obj=NULL, *spec2_obj = NULL;
	double n0;
	int ind;
	int m, bb0, ss1;

	vector<int> vec_max, vec_ss1, vec_bb0;
	//Parsing the inputs
	if (!PyArg_ParseTuple(args,"OOOOOOdi", &vec_power_obj, &vec_fd_obj, &vec_w_obj, &vec_snr_obj,&freq_obj,
	&spec2_obj, &n0, &ind)){ //Reference count not increased here
		return NULL;
	}


	//Parsing the type of inputs
	if (!PyList_Check(vec_power_obj)) return NULL;
	if (!PyList_Check(vec_fd_obj)) return NULL;
	if (!PyList_Check(vec_w_obj)) return NULL;
	if (!PyList_Check(vec_snr_obj)) return NULL;
	if (!PyList_Check(freq_obj)) return NULL;
	if (!PyList_Check(spec2_obj)) return NULL;


	//If vec_max_obj, vec_ss1_obj, vec_bb0_obj are lists new references to the input objects are created
	Py_INCREF(vec_power_obj);Py_INCREF(vec_fd_obj);Py_INCREF(vec_w_obj);Py_INCREF(vec_snr_obj);
	Py_INCREF(spec2_obj);

	//Here starts the real implementation of the algorithm

	vector< vector<int> > possible_signal;
	bool cond = true, cond2 = true;
	vector<int> bb, ss;

	double last_doppler_freq = 0.0;
	if (ind>0){
		last_doppler_freq = PyFloat_AsDouble(PyList_GetItem(vec_fd_obj, ind-1));//borrowed reference
	}

	int k=0;
	int spec2_size= (int)PyList_Size(spec2_obj);

	double *spec2_tmp = (double*)malloc(sizeof(double)*spec2_size);

	for(int i=0;i<spec2_size;i++){
		spec2_tmp[i] = PyFloat_AsDouble(PyList_GetItem(spec2_obj, i));
	}
	while(true){
		k++;
		// cout <<ind <<' '<<k++<<endl;
		m = GetMaxIndex(spec2_tmp, spec2_size);//borrowed reference

		//bb gets erased first in the function
		GetFirstLesserInRange(spec2_tmp, m, spec2_size, n0, bb);//borrowed reference
		if (bb.size() == 0){
			bb0 = spec2_size - 1;
		}
		else{
			bb0 = bb.front()-1;
			bb0 =  (bb0 < 0 )? 0 : bb0;
			bb0 = min(spec2_size-1, bb0);
			bb0 = max(bb0, m);
		}

		//ss gets erased first in the function
		GetFirstLesserInRange(spec2_tmp, 0, m+1, n0, ss);//borrowed reference
		if (ss.size()==0){
			ss1=0;
		}
		else{
			ss1 = ss.back()+1;
		}
		ss1 = min(ss1,m);

		if ((ind < 209)&&(ind>205)){
			//cout << (ind*1.5) << ' ' <<(-278.2708520260 + ss1*5.5103139) << ' '<<(-278.2708520260 + bb0*5.5103139)<<endl;
		}
		if (ind != 0){
			//cond = (m > (1.5 * max_previous_height)) or (m < (0.5*max_previous_height)); Corregir para que funcione, recordar que max=0 no es freq 0
			//cond2 = PyFloat_AsDouble(PyList_GetItem(spec2_obj, m)) <= n0;
			cond2 = spec2_tmp[m] <=n0;
			if (!cond2){
				vector<int> item;
				item.push_back(m); item.push_back(ss1); item.push_back(bb0);
				possible_signal.push_back(item);

			}
			for (int i=ss1; i<=bb0; i++){
				spec2_tmp[i]=0.0;
			}
		}


		if ((ind==0)||cond2) break;
	}
	free(spec2_tmp);

	if (!(ind==0)){
		int max_index=-200;
		double max_heuristic = -1.0;
		double max_dist = 0;
		bool continuar_linea = true;
		double dist, heuristic, area, area_noise;
		for(int i=0; i<possible_signal.size();i++){
			m = possible_signal[i][0];
			ss1 = possible_signal[i][1];
			bb0 = possible_signal[i][2];

			area = abs(GetSumInRange(spec2_obj, ss1, bb0+1)-(PyFloat_AsDouble(PyList_GetItem(spec2_obj, ss1))+\
			PyFloat_AsDouble(PyList_GetItem(spec2_obj, bb0)))/2.0);

			area_noise = abs((bb0-ss1)*n0);


			if (area >= 15 * area_noise) continuar_linea = false;

			vector<double> moments = CalcMomentValues(ss1, bb0, spec2_obj, freq_obj, n0, true, true, false);
			double fd = moments[1];
			dist = abs(fd - last_doppler_freq);

			if (dist==0.0){
				heuristic = DBL_MAX;
			}
			else{
				heuristic = area/dist;
			}

			if (heuristic > (max_heuristic)){
				max_heuristic = heuristic;
				max_index=i;
				max_dist = dist;
			}
		}



		///// hasta aca esta bien
		if (possible_signal.size() == 0){
			m = vec_max[ind-1];
			ss1 = vec_ss1[ind-1];
			bb0 = vec_bb0[ind-1];
		}
		else{
			if (continuar_linea){
				double diff = 1000;

				for(int i=0; i<possible_signal.size();i++){
					vector<double> moments = CalcMomentValues(ss1, bb0, spec2_obj, freq_obj, n0, true, true, false);
					double fd = moments[1];
					if(abs(fd-last_doppler_freq)<diff){
						max_index = i;
						diff = abs(fd-last_doppler_freq);
					}
				}
			}

			m = possible_signal[max_index][0];
			ss1 = possible_signal[max_index][1];
			bb0 = possible_signal[max_index][2];
		}
	}
	vec_max.push_back(m);	vec_ss1.push_back(ss1);	vec_bb0.push_back(bb0);

	//Calculo de momentos
	double power, fd, w;
	vector<double> moments = CalcMomentValues(ss1, bb0, spec2_obj, freq_obj, n0);
	power = moments[0];	fd = moments[1];	w = moments[2];


	double snr = ((GetSumInRange(spec2_obj, 0, spec2_size)/spec2_size)-n0)/n0 ;
	if (snr < 1.e-20) snr = 1.e-20;



	PyObject* item = Py_BuildValue("d", power);
	PyList_Append(vec_power_obj, item);
	Py_DECREF(item);
	item = NULL;

	item = Py_BuildValue("d", fd);
	PyList_Append(vec_fd_obj, item);
	Py_DECREF(item);
	item = NULL;

	item = Py_BuildValue("d", w);
	PyList_Append(vec_w_obj, item);
	Py_DECREF(item);
	item = NULL;

	item = Py_BuildValue("d", snr);
	PyList_Append(vec_snr_obj, item);
	Py_DECREF(item);
	item = NULL;


	//Decreasing all references counters used in the function
	Py_DECREF(vec_power_obj);Py_DECREF(vec_fd_obj);Py_DECREF(vec_w_obj);Py_DECREF(vec_snr_obj);
	Py_DECREF(spec2_obj);

	vec_power_obj = NULL;	vec_fd_obj = NULL;	vec_w_obj = NULL;	vec_snr_obj = NULL;
	spec2_obj = NULL;


	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef DetectMethods[]={
	{"DetectInSpectrogram", (PyCFunction)DetectSpectrumInSpectrogram, METH_VARARGS,
	"Detect spectrum in a spectrogram."},
	{NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initcDetectSpectrum(void){
	Py_InitModule("cDetectSpectrum", DetectMethods);
}
