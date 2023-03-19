#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import unicodedata
import json
import pandas as pd
import time
import random
from requests.models import Response


URL_SEARCH_BASE = 'https://www.webmotors.com.br/api/search/car?url=https://www.webmotors.com.br/carros/rs/toyota/yaris?estadocidade=Rio%20Grande%20do%20Sul&tipoveiculo=carros&kmate=30000&marca1=TOYOTA&modelo1=YARIS&precoate=100000&lkid=1038&actualPage='


class OfertaSeminovos:

    """DTO para uma oferta de carro seminovo na Webmotors."""

    def __init__(self, id, fipe, marca, modelo, carroceria, valor, ano_fabricacao, ano_modelo, km, transmissao, cor, versao, cidade, tipo_vendedor, link):
        self.id = id
        self.fipe = fipe
        self.marca = marca
        self.modelo = modelo
        self.carroceria = carroceria
        self.valor = valor
        self.ano_fabricacao = ano_fabricacao
        self.ano_modelo = ano_modelo
        self.km = km
        self.transmissao = transmissao
        self.cor = cor
        self.versao = versao
        self.cidade = cidade
        self.tipo_vendedor = tipo_vendedor
        self.link = link

    def oferta(self):
        return {
            'Ano Fabricacao': self.ano_fabricacao,
            'Ano Modelo': self.ano_modelo,
            'Cidade': self.cidade,
            'Cor': self.cor,
            'Fipe': self.fipe,
            'Id': self.id,
            'KM': self.km,
            'Marca': self.marca,
            'Modelo': self.modelo,
            'Carroceria': self.carroceria,
            'Tipo Vendedor': self.tipo_vendedor,
            'Transmissao': self.transmissao,
            'Valor': self.valor,
            'Versao': self.versao,
            'Link': self.link
        }

    def __str__(self):
        return json.dumps({k: v for k, v in self.__dict__.items() if not k.startswith("__")}, indent=4)


def turn_pages():
    cars = []
    page = 1
    webmotors = get_cars(page)

    while len(webmotors['SearchResults']) == 24:
        cars.extend(parse_cars(webmotors['SearchResults']))
        page += 1
        time.sleep(random.randint(2, 4))
        print(len(cars), page)
        webmotors = get_cars(page)

    if len(webmotors['SearchResults']) != 0:
        cars.extend(parse_cars(webmotors['SearchResults']))
        print(len(cars), page)

    to_csv(cars)


def get_cars(page):
    url = URL_SEARCH_BASE + str(page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    response = requests.request("GET", url, headers=headers)
    return json.loads(response.content)


def parse_cars(carList):
    index = 0
    treated_cars = []
    for car in carList:
        try:
            fipe = car['FipePercent']
        except Exception as exp:
            fipe = 666

        make = unicodedata.normalize(
            "NFD", car['Specification']['Make']['Value']).encode("ascii", "ignore")
        model = unicodedata.normalize(
            "NFD", car['Specification']['Model']['Value']).encode("ascii", "ignore")
        version = unicodedata.normalize(
            "NFD", car['Specification']['Version']['Value']).encode("ascii", "ignore")
        ports = car['Specification']['NumberPorts']
        ano_fabricacao = int(car['Specification']['YearFabrication'])
        ano_modelo = int(car['Specification']['YearModel'])
        carroceria = str(car['Specification']['BodyType'])
        id = car['UniqueId']
        link = 'https://www.webmotors.com.br/comprar/' + make.decode() + '/' + model.decode() + '/' + version.decode().replace(
            ' ', '-',) + '/' + str(ports) + '-portas/' + str(ano_fabricacao) + '-' + str(ano_modelo) + '/' + str(id)

        treated_car = OfertaSeminovos(
            ano_fabricacao=int(ano_fabricacao),
            ano_modelo=int(ano_modelo),
            cidade=car['Seller']['City'],
            cor=car['Specification']['Color']['Primary'],
            fipe=fipe,
            id=id,
            km=int(car['Specification']['Odometer']),
            marca=make,
            modelo=model,
            carroceria=carroceria,
            tipo_vendedor=car['Seller']['SellerType'],
            transmissao=car['Specification']['Transmission'],
            valor=int(car['Prices']['Price']),
            versao=version,
            link=link
        )
        treated_cars.append(treated_car.oferta())
        index += 1
    return treated_cars


def to_csv(cars):
    df = pd.DataFrame(data=cars)
    column_names = ['Id', 'Fipe', 'Marca', 'Modelo', 'Valor', 'Ano Fabricacao',
                    'Ano Modelo', 'KM', 'Transmissao', 'Cor', 'Versao', 'Cidade', 'Tipo Vendedor', 'Link']
    mydf = df.reindex(columns=column_names)
    mydf.to_csv(r'WebmotorsCars.csv', encoding='utf-8', index=False)


if __name__ == "__main__":
    turn_pages()
