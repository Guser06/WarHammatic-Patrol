#pragma once
#include <string>
#include <unordered_map>
using namespace std;
class Arma
{
public:
	string nombre; //Nombre del arma
	vector<string> claves; //Claves del arma
	unordered_map<string, vector<string>> stats; //Equivalente de diccionario de stats
	bool usado; //Indica si el arma ya fue usada en el turno actual

	Arma(unordered_map<string, vector<string>> &diccionario, vector<string> &Texto){
		this->nombre = diccionario["Nombre"][0];
		for (size_t i = 0; i < Texto.size(); i++)
			this->stats[Texto[i]].push_back(diccionario["Stats"][i]); //Llena el diccionario de stats
		this->claves = diccionario["Claves"];
		this->usado = false;
	}

	void reboot() { this->usado = false; }
};
