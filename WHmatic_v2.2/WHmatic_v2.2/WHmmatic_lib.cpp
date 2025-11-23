
#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <vector>
#include <optional>
#include <iostream> 
#include <random>
#include <chrono>
#include <string>
#include <unordered_map>
using namespace std;


class Elemento
{
public:
	sf::Vector2f posicion;
	std::string Texto;
	sf::Texture textura;
	virtual ~Elemento() {};
};

class Boton : public Elemento
{
public:
	sf::Vector2f tamano;
	bool presionado = false;
	sf::RectangleShape rect;
	sf::Sprite* sprite = nullptr;
	Boton(sf::Vector2f pos, sf::Vector2f tam, std::string texto)
	{
		this->presionado = false;
		this->posicion = pos;
		this->tamano = tam;
		this->Texto = texto;
		this->rect.setSize(tam);
		this->rect.setPosition(pos);
	}
	Boton(sf::Vector2f pos, sf::Vector2f tam, sf::Texture tex)
	{
		this->presionado = false;
		this->posicion = pos;
		this->tamano = tam;
		this->sprite = new sf::Sprite(tex);
	}
	virtual ~Boton() { delete this->sprite; }
};

class Arma
{
public:
	string nombre; //Nombre del arma
	vector<string> claves; //Claves del arma
	unordered_map<string, vector<string>> stats; //Equivalente de diccionario de stats
	bool usado; //Indica si el arma ya fue usada en el turno actual

	Arma(unordered_map<string, vector<string>>& diccionario, vector<string>& Texto) {
		this->nombre = diccionario["Nombre"][0];
		for (size_t i = 0; i < Texto.size(); i++)
			this->stats[Texto[i]].push_back(diccionario["Stats"][i]); //Llena el diccionario de stats
		this->claves = diccionario["Claves"];
		this->usado = false;
	}

	void reboot() { this->usado = false; }
};

class Individuo : public Arma
{
public:

};

vector<unordered_map<string, vector<string>>> ElegirEjercitos(sf::RenderWindow& Ventana) {
	vector<unordered_map<string, vector<string>>> ejercitos;
	Ventana.clear(sf::Color::Black);
	vector<string> opts;
	for (size_t i = 0; i < opts.size(); i++)
	{
		Boton
	}
	return ejercitos;
}
