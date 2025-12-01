#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include "json.hpp"
#include "clases.hpp"
#include <vector>
#include <optional>
#include <iostream>
#include <fstream>
#include <random>
#include <chrono>
#include <string>
#include <map>
#include <cstdlib>
#include <ctime>
#include <numeric>

using namespace std;
using json = nlohmann::json;

vector< Ejercito > ElegirEjercitos(Ventana& v) {
	map<string, string> opts;
	opts.insert({"Tyranidos Pesados", "Ty_Tyrannofex.json" });
	opts.insert({ "Marines Pesados", {"UM_Lancer.json"}});
	opts.insert({ "Tyranidos", {"Ty_patrol.json"} });
	opts.insert({ "Marines", {"UM_patrol.json"} });
	int indice = 0;
	vector < Ejercito > ejercitos;

	v.ventana->clear(sf::Color::Black);
	for (auto i: opts)
	{
		Boton* B = new Boton(sf::Vector2f({indice*60, 0}), sf::Vector2f({60, 180}), i.first);
		v.elementos.push_back(B);
		indice++;
		v.ventana->draw(B->rect);
	}
	
	while (const std::optional ev = v.ventana->pollEvent())
	{
		if (ejercitos.size() >= 2)
			break;
		if (ev->is<sf::Event::Closed>())
			v.ventana->close();
		else if (const auto* tecla = ev->getIf<sf::Event::KeyPressed>())
			if (tecla->scancode == sf::Keyboard::Scancode::Escape)
				v.ventana->close();
		else if (const auto* click = ev->getIf<sf::Event::MouseButtonPressed>())
		{
			v.PosMouse = sf::Mouse::getPosition(*(v.ventana));
			int PosY = v.PosMouse.y / 60;

			if (click->button == sf::Mouse::Button::Left)
			{
				Boton* B = dynamic_cast<Boton*>(v.elementos[PosY]);
				B->presionado = true;
			}
		}
        for (auto& e : v.elementos)
        {
            Boton* B = dynamic_cast<Boton*>(e);
            if (B->presionado)
            {
                Ejercito nE;
                std::ifstream archivo("sprites/" + opts[B->Texto]);
				json j;
                archivo >> j;
                from_json(j, nE);
				ejercitos.push_back(nE);
				B->presionado = false;
            }
        }
	}

	v.elementos.clear();
	return ejercitos;
}

vector<int> Dados(int n_dados, int Dx, bool ret_num)
{
	vector<int> res_dados;
	for (int i = 0; i < n_dados; i++)
	{
		srand(time(NULL));
		int resultado = (rand()%Dx)+1;
		res_dados.push_back(resultado);
	}
	return res_dados;
}

int Dados(int n_dados, int Dx)
{
	vector<int> res_dados;
	for (int i = 0; i < n_dados; i++)
	{
		srand(time(NULL));
		int resultado = (rand() % Dx) + 1;
		res_dados.push_back(resultado);
	}
	return accumulate(res_dados.begin(), res_dados.end(), 0);
}

vector<int> AtkDmg_Rand(string nDx)
{
	vector<int> resultados;
	size_t pos_D = nDx.find('D');
	size_t pos_plus = nDx.find('+');

	string sub_s = nDx.substr(0, pos_D);
	int cantidad;

	if (sub_s == "")
		cantidad = 1;
	else
		cantidad = stoi(sub_s);
	cantidad = Dados(cantidad, stoi(nDx.substr(pos_D+1, pos_plus - pos_D+1)));
	if (pos_plus != string::npos)
		cantidad += stoi(nDx.substr(pos_plus + 1));
	resultados = Dados(cantidad, stoi(nDx.substr(pos_D+1, pos_plus - pos_D + 1)), false);	
	return resultados;
}

int AtkDmg_Rand(string nDx, bool dmg)
{
	size_t pos_D = nDx.find('D');
	size_t pos_plus = nDx.find('+');

	string sub_s = nDx.substr(0, pos_D);
	int cantidad;

	if (sub_s == "")
		cantidad = 1;
	else
		cantidad = stoi(sub_s);
	cantidad = Dados(cantidad, stoi(nDx.substr(pos_D + 1, pos_plus - pos_D + 1)));
	if (pos_plus != string::npos)
		cantidad += stoi(nDx.substr(pos_plus + 1));
	return cantidad;
}

vector<int> RepFallos(vector<int> tiradas, int val, int Dx)
{
	vector<int> exito;
	vector<int> nuevos;
	for (auto t : tiradas)
		if (t >= val)
			exito.push_back(t);
	nuevos = Dados(tiradas.size() - exito.size(), Dx);
	exito.insert(exito.end(), nuevos.begin(), nuevos.end());
	return exito;
}

int RepFallos(vector<int> tiradas, int val, int Dx, bool ret_num)
{
	vector<int> exito;
	vector<int> nuevos;
	for (auto t : tiradas)
		if (t >= val)
			exito.push_back(t);
	nuevos = Dados(tiradas.size() - exito.size(), Dx);
	exito.insert(exito.end(), nuevos.begin(), nuevos.end());
	return accumulate(exito.begin(), exito.end(), 0);
}

void Aumentar_PC(vector<Ejercito> Ejs)
{
	for (auto& ej : Ejs)
		ej.pc += 1;
	return;
}

void Aumentar_Mov_Atk(Ejercito Ej)
{
	for (auto& u : Ej.unidades)
		u.mov = 3;
		u.atk = 3;
	return;
}

void Shock_Test(Unidad& U, Ventana& v)
{
	v.ventana->clear(sf::Color::Black);
	if ((U.miembros.size() < U.nm / 2) && (U.nm != 1))
	{
		int mayor = 0;
		for (auto& m : U.miembros)
			if (m.stats_map["Liderazgo"] > mayor)
				mayor = m.stats_map["Liderazgo"];
		int prueba = Dados(2, 6);
		if (prueba < mayor)
		{
			U.shock = true;

		}
	}
}