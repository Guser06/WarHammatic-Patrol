#pragma once
#include <SFML/Graphics.hpp>
#include <string>
class Elemento
{
public:
	sf::Vector2f posicion;
	std::string Texto;
	sf::Texture textura;
	virtual ~Elemento() {};
};

