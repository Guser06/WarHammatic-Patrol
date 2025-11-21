#pragma once
#include "Elemento.h"
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

