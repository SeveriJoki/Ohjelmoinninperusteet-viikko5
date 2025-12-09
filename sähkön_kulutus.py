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

    current_date = datetime.min
    viikon_tiedot = []
    #paivan_tiedot formaatti: Viikonpäivä, päivämäärä, k1,k2,k3, t1,t2,t3
    paivan_tiedot = [""] + [sahkonkulutus[0][0]] + [0] * (len(sahkonkulutus[0])-1)

    #refactoroin tämän kohdan vielä. 9.12
    for sahkotunti in sahkonkulutus:
        sahkotunnin_date = sahkotunti[0]
        if current_date.date() != sahkotunnin_date.date():
            if paivan_tiedot[0] != "":
                viikon_tiedot.append(paivan_tiedot)
                paivan_tiedot = [""] + [sahkotunnin_date] + [0] * (len(sahkonkulutus[0])-1)
            current_date = sahkotunnin_date
            paivan_tiedot[0] = VIIKONPAIVAT[current_date.weekday()]
        for i, obj in enumerate(sahkotunti[1:], start=1):
            paivan_tiedot[i+1] += obj
    viikon_tiedot.append(paivan_tiedot)

    #muutetaan datetime ja floatit tulostettavaan muotoon sekä kWh pyöristetään 2 merkitsevän tarkkuudella.
    for paiva in viikon_tiedot:
        paiva_str = paiva[1].strftime("%d-%m-%Y")
        paiva_str = paiva_str.replace("-", ".")
        paiva[1] = paiva_str
        
        for i, kwh in enumerate(paiva[2:], start=2):
            paiva[i] = round(kwh, 2)
            paiva[i] = str(paiva[i])
            paiva[i] = paiva[i].replace(".", ",")
        
    return viikon_tiedot

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

    for rivi in tasoitetut_tiedot:
        print(rivi)

if __name__ == "__main__":
    main()