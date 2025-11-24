#include <SFML/Graphics.hpp>
#include <SFML/Window.hpp>
#include <vector>
#include <optional>
#include <iostream> 
#include <random>
#include <chrono>
#include <string>
#include <map>
using namespace std;

//Clase base para los elementos de la interfaz
class Elemento
{
public:
	sf::Vector2f posicion;
	std::string Texto;
	sf::Texture textura;
	virtual ~Elemento() {};
	virtual string Type() {};
};

//Clase botón para la interfaz
class Boton : public Elemento
{
public:
	sf::Vector2f tamano;
	bool presionado = false;
	sf::RectangleShape rect;
	sf::Sprite* sprite = nullptr;
	sf::Font* font = nullptr;
	sf::Text* textoBoton;
	Boton(sf::Vector2f pos, sf::Vector2f tam, string texto)
	{
		this->presionado = false;
		this->posicion = pos;
		this->tamano = tam;
		this->Texto = texto;
		this->rect.setSize(this->tamano);
		this->rect.setPosition(this->posicion);
		this->font = new sf::Font();
		this->font->openFromFile("sprites/ARIAL.TTF");
		this->textoBoton->setString("Reintentar?");
		this->textoBoton->setCharacterSize(24);
		this->textoBoton->setFillColor(sf::Color::Black);
		this->textoBoton->setPosition(pos);
	}
	Boton(sf::Vector2f pos, sf::Vector2f tam, sf::Texture tex)
	{
		this->presionado = false;
		this->posicion = pos;
		this->tamano = tam;
		this->sprite = new sf::Sprite(tex);
	}
	bool CheckClick(sf::Vector2i PosM) {
		if (PosM.x >= this->posicion.x && PosM.x <= this->posicion.x + this->tamano.x &&
			PosM.y >= this->posicion.y && PosM.y <= this->posicion.y + this->tamano.y)
		{
			this->presionado = true;
		}
		else
			this->presionado = false;
		return this->presionado;
	}
	virtual ~Boton() { delete this->sprite; }
	virtual string Type() override { return "Boton"; }
};

class Ventana
{
public:
	sf::RenderWindow* ventana = nullptr;
	vector<Elemento*> elementos;
	sf::Vector2i PosMouse;
	Ventana(int Ancho, int Alto, string Nombre)
	{
		this->ventana = new sf::RenderWindow(sf::VideoMode({ Ancho, Alto }), Nombre);
		this->ventana->setFramerateLimit(60);
	}
	virtual ~Ventana() {
		delete this->ventana;
		for (size_t i = 0; i < this->elementos.size(); i++)
			delete this->elementos[i];
	}
	string Type() { return "Ventana"; }
};

class Arma
{
public:
	string nombre; //Nombre del arma
	vector<string> claves; //Claves del arma
	map<string, vector<string>> stats; //Equivalente de diccionario de stats
	bool usado; //Indica si el arma ya fue usada en el turno actual

	Arma(map<string, vector<string>>& diccionario, vector<string>& ArmaTx) {
		this->nombre = diccionario["Nombre"][0];
		for (size_t i = 0; i < ArmaTx.size(); i++)
			this->stats[ArmaTx[i]].push_back(diccionario["Stats"][i]); //Llena el diccionario de stats
		this->claves = diccionario["Claves"];
		this->usado = false;
	}

	void reboot() { this->usado = false; }
	string Type() { return "Arma"; }
};

class Individuo : public Arma, public Elemento
{
public:
	vector<Arma> Melee; //Armas cuerpo a cuerpo
	vector<Arma> Rango; //Armas a distancia
	int dmg = 0; //Daño recibido

	Individuo (map<string, map<string, vector<string> > > & diccionario, vector<string>& StatsTx, int nM) :
		Arma(diccionario["m" + to_string(nM)], StatsTx)
	{
		this->usado = true;

	}
	string Type() override { return "Individuo"; }
};

vector<map<string, vector<string>>> ElegirEjercitos(Ventana& v) {
	map<string, vector<string>> opts;
	opts.insert({"Tyranidos Pesados", {"EnjambresDevoradores.json", "Espinogantes.json", 
								"Psicofago.json", "SaltadoresVonRyan.json", "Termagantes.json",
								"Termagantes.json", "TyranidoPrimus.json", "Tyrannofex.json"} });
	opts.insert({ "Marines Pesados", {"BibliotecarioExterminador.json", "CapitanExterminador.json",
								"Exterminadores.json", "Infernus.json", "Lancer.json",
								"Techmarine.json"}});
	opts.insert({ "Tyranidos", {"EnjambresDevoradores.json", "Espinogantes.json",
								"Psicofago.json", "SaltadoresVonRyan.json", "Termagantes.json",
								"Termagantes.json", "TyranidoPrimus.json"} });
	opts.insert({ "Marines Pesados", {"BibliotecarioExterminador.json", "CapitanExterminador.json",
								"Exterminadores.json", "Infernus.json"} });
	int indice = 0;
	vector < map < string, vector < string > > > ejercitos;

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
	}

	for (auto& e : v.elementos)
	{
		Boton* B = dynamic_cast<Boton*>(e);
		if (B->presionado)
		{
			map < string, vector < string > > temp;
			temp.insert({ B->Texto, opts[B->Texto] });
			ejercitos.push_back(temp);
		}
	}

	v.elementos.clear();
	return ejercitos;
}
