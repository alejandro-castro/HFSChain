#include <Python.h>
// #include <numpy/arrayobject.h>
#include <vector>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <cfloat>
using namespace std;


static int GetMaxIndex(double* array, int size){
	double max = *array;
	int ind = 0;

	for (int i=0;i< size; i++){
		if (array[i]>max){
			max=array[i];
			ind = i;
		}
	}
	return ind;
}


static void GetFirstLesserInRange(double* array, int start, int end, double threshold,
	vector<int> &result){

	for (int i=start; i< end; i++){
		if (array[i] < threshold) {
			result.push_back(i);
		}
	}
}

static double GetSumInRange(double *array, int start, int end){
	double result=0;
	for(int i=start; i<end; i++){
		result = result + array[i];
	}
	return result;
}
static PyObject *DetectSpectrumInSpectrogram(PyObject *self, PyObject *args){
	// The first three parameters should be PyObjects only because we wanted to modified them
	PyObject *vec_max_obj, *vec_ss1_obj, *vec_bb0_obj, *spec2_obj, *spec2_tmp;
	double *spec2;
	double n0;
	int ind;
	int m, bb0, ss1;

	//Parsing the inputs
	if (!PyArg_ParseTuple(args,"OOOOdi", &vec_max_obj, &vec_ss1_obj, &vec_bb0_obj,
	&spec2_obj, &n0, &ind)){ //Reference count not increased here
		return NULL;
	}

	// if (ind==0) cout <<"yes"<<endl;
	// cout <<"nooo"<<endl;
	//
	//
	// Py_INCREF(Py_None);
	// return Py_None;

	//Parsing the type of inputs
	if (!PyList_Check(vec_max_obj)) return NULL;
	if (!PyList_Check(vec_ss1_obj)) return NULL;
	if (!PyList_Check(vec_bb0_obj)) return NULL;
	if (!PyList_Check(spec2_obj)) return NULL;


	//If vec_max_obj, vec_ss1_obj, vec_bb0_obj are lists new references to the input objects are created
	Py_INCREF(vec_max_obj);Py_INCREF(vec_ss1_obj);Py_INCREF(vec_bb0_obj);
	Py_INCREF(spec2_obj);

	spec2 = (double*)spec2_obj;
	// change the requirement argument if you want to filter the spectre here
	// spec2_tmp = PyArray_FROM_OTF(spec2_obj, NPY_FLOAT64, NPY_ARRAY_IN_ARRAY); //Return a new reference o new object
	// if (spec2_tmp == NULL){
	// 	Py_DECREF(vec_max_obj);Py_DECREF(vec_ss1_obj);Py_DECREF(vec_bb0_obj);
	// 	Py_DECREF(spec2_obj);
	//
	// 	return NULL;
	// }

	//spec2 =(double*)PyArray_DATA(spec2_tmp); // borrowed reference from spec2_tmp, so it is not necessary to create a new one
	Py_INCREF(spec2);
	//Here starts the real implementation of the algorithm

	vector< vector<int> > possible_signal;
	bool cond = true, cond2 = true;
	vector<int> bb, ss;

	int max_previous_height = (int)PyInt_AsLong(PyList_GetItem(vec_max_obj, ind-1));//borrowed reference

	int k=0;
	while(true){
		k++;
		// cout <<ind <<' '<<k++<<endl;
		int spec2_size= (int)PyList_Size(spec2_obj);

		m = GetMaxIndex(spec2, spec2_size);//borrowed reference
		//cout<<m<<' '<<spec2_size<<endl;


		GetFirstLesserInRange(spec2, m, spec2_size, n0, bb);//borrowed reference
		if (bb.size() == 0){
			bb0 = spec2_size - 1;
		}
		else{
			bb0 = bb.front()-1;
			bb0 =  (bb0 < 0 )? 0 : bb0;
			bb0 = min(spec2_size-1, bb0);
			bb0 = max(bb0, m);
		}

		GetFirstLesserInRange(spec2, 0, m+1, n0, ss);//borrowed reference
		if (ss.size()==0){
			ss1=0;
		}
		else{
			ss1 = ss.back()+1; //*max_element(ss.begin(), ss.end())+1 ;
		}
		ss1 = min(ss1,m);


		// if (k==1) cout <<"el problema "<< ss1 <<' '<< bb0<<endl;
		if (ind != 0){
			cond = (m > (1.05 * max_previous_height)) or (m < (0.95*max_previous_height));
			cond2 = spec2[m] <= n0;
			if (!cond2){
				vector<int> item;
				item.push_back(m); item.push_back(ss1); item.push_back(bb0);
				possible_signal.push_back(item);
			}
			for (int i=ss1; i<=bb0; i++){
				spec2[i] = 0.0;
			}
		}
		// if ((ind==203) &&(k==601)){
		// 	cout <<n0<<' '<< ss1 <<' '<< bb0<<endl;
		// 	for (int j=0;j<spec2_size;j++){
		// 		cout<<'g'<<spec2[j]<<'g'<<' ';
		// 	}
		// }

		if ((ind==0)||(!cond)||cond2) break;
	}

	if (!(ind==0)){
		int max_index=-200;
		double max_heuristic = -1.0;
		bool continuar_linea = true;

		for(int i=0; i<possible_signal.size();i++){
			m = possible_signal[i][0];
			ss1 = possible_signal[i][1];
			bb0 = possible_signal[i][2];

			double area = abs(GetSumInRange(spec2, ss1, bb0+1)-(spec2[ss1]+spec2[bb0])/2.0);

			double area_noise = abs((bb0-ss1)*n0);


			if (area < 15 * area_noise)	area = 1e-15;
			else continuar_linea = false;


			double dist = abs(m - max_previous_height);
			double heuristic;

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

		if (possible_signal.size() == 0){
			m = (int)PyInt_AsLong(PyList_GetItem(vec_max_obj, ind-1));
			ss1 = (int)PyInt_AsLong(PyList_GetItem(vec_ss1_obj, ind-1));
			bb0 = (int)PyInt_AsLong(PyList_GetItem(vec_bb0_obj, ind-1));
		}
		else{
			m = possible_signal[max_index][0];
			ss1 = possible_signal[max_index][1];
			bb0 = possible_signal[max_index][2];
		}
	}
	//printf ("%d %d %d", m, bb0, ss1);
	PyList_Append(vec_max_obj, Py_BuildValue("i", m));
	PyList_Append(vec_bb0_obj, Py_BuildValue("i", bb0));
	PyList_Append(vec_ss1_obj, Py_BuildValue("i", ss1));




	//Decreasing all references counters used in the function
	Py_DECREF(vec_max_obj);Py_DECREF(vec_ss1_obj);Py_DECREF(vec_bb0_obj);
	Py_DECREF(spec2_obj);

	//Py_DECREF(spec2_tmp);

	Py_DECREF(spec2);
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
	//import_array();
}
