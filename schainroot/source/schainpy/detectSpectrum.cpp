#include <Python.h>
#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <cfloat>
using namespace std;


static int GetMaxIndex(PyObject* array, int size){
	double max = PyFloat_AsDouble(PyList_GetItem(array, 0));
	int ind = 0;

	double value;
	for (int i=0;i< size; i++){
		value = PyFloat_AsDouble(PyList_GetItem(array, i));
		if (value>max){
			max=value;
			ind = i;
		}
	}
	return ind;
}


static void GetFirstLesserInRange(PyObject* array, int start, int end, double threshold,
	vector<int> &result){

	for (int i=start; i< end; i++){
		if (PyFloat_AsDouble(PyList_GetItem(array, i)) < threshold) {
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
static PyObject *DetectSpectrumInSpectrogram(PyObject *self, PyObject *args){
	// The first three parameters should be PyObjects only because we wanted to modified them
	PyObject *vec_max_obj = NULL, *vec_ss1_obj = NULL, *vec_bb0_obj = NULL, *spec2_obj = NULL;
	double n0;
	int ind;
	int m, bb0, ss1;

	//Parsing the inputs
	if (!PyArg_ParseTuple(args,"OOOOdi", &vec_max_obj, &vec_ss1_obj, &vec_bb0_obj,
	&spec2_obj, &n0, &ind)){ //Reference count not increased here
		return NULL;
	}


	//Parsing the type of inputs
	if (!PyList_Check(vec_max_obj)) return NULL;
	if (!PyList_Check(vec_ss1_obj)) return NULL;
	if (!PyList_Check(vec_bb0_obj)) return NULL;
	if (!PyList_Check(spec2_obj)) return NULL;


	//If vec_max_obj, vec_ss1_obj, vec_bb0_obj are lists new references to the input objects are created
	Py_INCREF(vec_max_obj);Py_INCREF(vec_ss1_obj);Py_INCREF(vec_bb0_obj);
	Py_INCREF(spec2_obj);

	//Here starts the real implementation of the algorithm

	vector< vector<int> > possible_signal;
	bool cond = true, cond2 = true;
	vector<int> bb, ss;

	int max_previous_height = 0;
	if (ind>0){
		max_previous_height = (int)PyInt_AsLong(PyList_GetItem(vec_max_obj, ind-1));//borrowed reference
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
		m = GetMaxIndex(spec2_obj, spec2_size);//borrowed reference

		GetFirstLesserInRange(spec2_obj, m, spec2_size, n0, bb);//borrowed reference
		if (bb.size() == 0){
			bb0 = spec2_size - 1;
		}
		else{
			bb0 = bb.front()-1;
			bb0 =  (bb0 < 0 )? 0 : bb0;
			bb0 = min(spec2_size-1, bb0);
			bb0 = max(bb0, m);
		}

		GetFirstLesserInRange(spec2_obj, 0, m+1, n0, ss);//borrowed reference
		if (ss.size()==0){
			ss1=0;
		}
		else{
			ss1 = ss.back()+1;
		}
		ss1 = min(ss1,m);

		if ((ind < 209)&&(ind>205)){
			cout << (ind*1.5) << ' ' <<(-278.2708520260 + ss1*5.5103139) << ' '<<(-278.2708520260 + bb0*5.5103139)<<endl;
		}
		if (ind != 0){
			//cond = (m > (1.5 * max_previous_height)) or (m < (0.5*max_previous_height)); Corregir para que funcione, recordar que max=0 no es freq 0
			cond2 = PyFloat_AsDouble(PyList_GetItem(spec2_obj, m)) <= n0;
			if (!cond2){
				vector<int> item;
				item.push_back(m); item.push_back(ss1); item.push_back(bb0);
				possible_signal.push_back(item);
			}
			for (int i=ss1; i<=bb0; i++){
				PyList_SetItem(spec2_obj, i, Py_BuildValue("d", 0.0));
			}
		}


		if ((ind==0)||cond2) break;
	}
	if (!(ind==0)){
		int max_index=-200;
		double max_heuristic = -1.0;
		bool continuar_linea = true;
		double dist, heuristic;
		for(int i=0; i<possible_signal.size();i++){
			m = possible_signal[i][0];
			ss1 = possible_signal[i][1];
			bb0 = possible_signal[i][2];

			double area = abs(GetSumInRange(spec2_obj, ss1, bb0+1)-(PyFloat_AsDouble(PyList_GetItem(spec2_obj, ss1))+\
			PyFloat_AsDouble(PyList_GetItem(spec2_obj, bb0)))/2.0);

			double area_noise = abs((bb0-ss1)*n0);


			if (area >= 15 * area_noise) continuar_linea = false;


			dist = abs(m - max_previous_height);

			if (dist==0){
				heuristic = DBL_MAX;
			}
			else{
				heuristic = area/dist;
			}

			if (heuristic>max_heuristic){
				max_heuristic = heuristic;
				max_index=i;
			}
		}



		///// hasta aca esta bien
		if (possible_signal.size() == 0){
			m = (int)PyInt_AsLong(PyList_GetItem(vec_max_obj, ind-1));
			ss1 = (int)PyInt_AsLong(PyList_GetItem(vec_ss1_obj, ind-1));
			bb0 = (int)PyInt_AsLong(PyList_GetItem(vec_bb0_obj, ind-1));
		}
		else{
			if (continuar_linea){
				double diff = 1000;

				for(int i=0; i<possible_signal.size();i++){
					m = possible_signal[i][0];
					if(abs(m-max_previous_height)<diff){
						max_index = i;
						diff = abs(m-max_previous_height);
					}
				}
			}

			m = possible_signal[max_index][0];
			ss1 = possible_signal[max_index][1];
			bb0 = possible_signal[max_index][2];
		}
	}
	//printf ("%d %d %d", m, bb0, ss1);
	PyObject* item = Py_BuildValue("i", m);
	PyList_Append(vec_max_obj, item);
	Py_DECREF(item);
	item = NULL;

	item = Py_BuildValue("i", bb0);
	PyList_Append(vec_bb0_obj, item);
	Py_DECREF(item);
	item = NULL;

	item = Py_BuildValue("i", ss1);
	PyList_Append(vec_ss1_obj, item);
	Py_DECREF(item);
	item = NULL;


	//Decreasing all references counters used in the function
	Py_DECREF(vec_max_obj);Py_DECREF(vec_ss1_obj);Py_DECREF(vec_bb0_obj);
	Py_DECREF(spec2_obj);

	vec_max_obj = NULL;	vec_ss1_obj = NULL;	vec_bb0_obj = NULL;	spec2_obj = NULL;


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
