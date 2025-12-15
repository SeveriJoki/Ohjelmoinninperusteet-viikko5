# Copyright (c) 2025 Severi Joki
# License: MIT

from datetime import datetime

VIIKONPAIVAT = {
    0:"Maanantai",
    1:"Tiistai",
    2:"Keskiviikko",
    3:"Torstai",
    4:"Perjantai",
    5:"Lauantai",
    6:"Sunnuntai"
}
def muunna_sahkotiedot(sahkotunti: list):
    """muutetaan tiedot oikeisiin muotoon. Valmistellaan datetime myös oikeaaseen formaattiin."""
    a = sahkotunti[0].replace("T", " ")
    aika = datetime.strptime(a, "%Y-%m-%d %H:%M:%S")
    muutettu_sahkotunti = []
    muutettu_sahkotunti.append(aika)
    muutettu_sahkotunti.append(float(sahkotunti[1]) / 1000)
    muutettu_sahkotunti.append(float(sahkotunti[2]) / 1000)
    muutettu_sahkotunti.append(float(sahkotunti[3]) / 1000)
    muutettu_sahkotunti.append(float(sahkotunti[4]) / 1000)
    muutettu_sahkotunti.append(float(sahkotunti[5]) / 1000)
    muutettu_sahkotunti.append(float(sahkotunti[6]) / 1000)
    return muutettu_sahkotunti

def hae_sahkonkulutus(sahkotiedosto: str) -> list:
    """
    avataan tiedosto ja palautetaan tiedot matriisissa valmiina oikeissa muodoissa.
    Samana viikonpäivänä oleva data summataan ja lisätään viikonpäivät päivämäärän lisäksi.
    """

    sahkonkulutus = []
    with open(sahkotiedosto, "r", encoding="utf-8") as f:
        next(f)
        for tiedot in f:
            tiedot = tiedot.strip()
            sahkotunti = tiedot.split(';')
            sahkonkulutus.append(muunna_sahkotiedot(sahkotunti))


    #sahkonkulutus rivin formaatti == [datetime, k1,k2,k3, t1,t2,t3]
    #paivan_tiedot on dictionary jossa avain on päivämäärä ja arvot ovat k1,k2,k3,t1,t2,t2
    paivan_tiedot = {}
    for row in sahkonkulutus:
        dt = row[0].date()
        values = row[1:]

        if dt not in paivan_tiedot:
            paivan_tiedot[dt] = [0] * len(values)
        
        for i, val in enumerate(values):
            paivan_tiedot[dt][i] += val

    #laitetaan tiedot tulostettavaan muotoon.
    #lisätään viikonpäivä ennen päivänäärää
    #muutetaan pilkut pisteiksi
    results = []
    for dt in sorted(paivan_tiedot.keys()):
        values = paivan_tiedot[dt]
        viikonpaiva = VIIKONPAIVAT[dt.weekday()]
        date_str = dt.strftime("%d.%m.%Y")
        formatted_values = [format(round(v, 2), ".2f").replace(".",",")
                             for v in values]
        results.append([viikonpaiva, date_str] + formatted_values)
 
        
    return results

def tasoita_lista(nested: list):
    """Palautta tasoitetun listan sukeltaa sublistoihin tarvittaessa."""
    
    tulos = []

    def sukella(lista: list):
        """
        Kulkee yhden iteraation alaspäin nested listassa ja tarvittaessa enemmän.
        Palauttaa kaikki muuttujat ryhmiteltynä listoissa "tulos" listaan.
        """
        current = []
        for obj in lista:
            if isinstance(obj, list): #jos osutaan listaan ja currentissa on dataa tallennetaan ne "tulos" muuttujaan
                if current:
                    tulos.append(current)
                    current = []
                sukella(obj) #uusi lista löytyi mennään syvemmälle
            else:
                current.append(obj)
        #listat käyty läpi, tallennetaan viimeiset muuttujat "tulos" muuttujaan
        if current:
            tulos.append(current)

    sukella(nested)
    return tulos

def tasoita_sarakkeet(*listat: list):
    """
    Ottaa useita listoja ja tasoittaa sarakkeet yhtä leveiksi.
    Tämä varmistaa listojen tulostaessa olevan samoissa sijainneissa.
    luo myös kaikkien syötettyjen paremetrien väliin jakaja viivan.
    """
    tasoitetut_listat = []

    for lista in listat:
        tasoitetut_listat.extend(tasoita_lista(lista))

    sarakkeiden_suurimmat_leveydet =  [0] * (len(tasoitetut_listat[0]))
    padding = " "

    for lista in tasoitetut_listat:
        for i, item in enumerate(lista):
            if len(item) > sarakkeiden_suurimmat_leveydet[i]:
                sarakkeiden_suurimmat_leveydet[i] = len(item)
    for lista in tasoitetut_listat:
        for i,item in enumerate(lista):
            if sarakkeiden_suurimmat_leveydet[i] > len(item):
                lisattava_pituus = sarakkeiden_suurimmat_leveydet[i] - len(item)
                lista[i] = item + padding * lisattava_pituus

    for lista in tasoitetut_listat:
        for i, item in enumerate(lista):
            lista[i] = lista[i] + padding*3
                
    

    #Luodaan jakaja viiva laitetaan se oikeaaseen sijaintiin
    viiva = "-"
    jakaja_viiva = ""
    for solu_pituus in sarakkeiden_suurimmat_leveydet:
        jakaja_viiva += viiva * solu_pituus + viiva * 4

    parametrien_pituudet = []
    for lista in listat:
        parametrien_pituudet.append(len(lista))
    for sijainti in parametrien_pituudet[:-1]:
        tasoitetut_listat.insert(sijainti, jakaja_viiva)


    return tasoitetut_listat

def tulosta_tiedot(tiedot:list[str,int]):

    for row in tiedot:
        if isinstance(row, list):
            print(*row)
        else:
            print(row)
    return

def main():
    """
    Hankitaan sähkönkulutuksen tiedot ja ennen tulostamista tarkistetaan rivien koot.
    Tehdään jokaisesta sarakkeesta yhtä leveitä, joka tekee lukemisesta paljon helpompaa.
    Sarakkeiden leveyksien valmistelun jälkeen tulostetaan koko sähköviikko
    """
    sahkon_kulutustiedot = hae_sahkonkulutus("viikko42.csv")

    tulostus_rivi1 = ["Päivä", "Pvm",    "Kulutus", "[kWh]", "",  "Tuotanto", "[kWh]",  ""]
    tulostus_rivi2 = ["",  "(pv.kk.vvvv)", "v1",    "v2",   "v3", "v1",      "v2",    "v3" ]
    tulostus_otsikot = []
    tulostus_otsikot.append(tulostus_rivi1)
    tulostus_otsikot.append(tulostus_rivi2)

    tasoitetut_tiedot = []
    tasoitetut_tiedot = tasoita_sarakkeet(tulostus_otsikot, sahkon_kulutustiedot)

    tulosta_tiedot(tasoitetut_tiedot)


if __name__ == "__main__":
    main()