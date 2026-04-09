-- Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- https://www.postgresql.org/docs/current/sql-insert.html

-- Autohäuser einfügen
INSERT INTO autohaus (
    version, name, anzahl_fahrzeuge, gruendungsdatum, homepage, telefonnummer, erzeugt, aktualisiert
) VALUES (
    0, 'Porsche Zentrum Stuttgart', 3, '1995-03-15', 'https://www.porsche-stuttgart.de', '+49 711 5555-100', NOW(), NOW()
);

INSERT INTO autohaus (
    version, name, anzahl_fahrzeuge, gruendungsdatum, homepage, telefonnummer, erzeugt, aktualisiert
) VALUES (
    0, 'Ferrari Europa München', 3, '2005-06-20', 'https://www.ferrari-muenchen.de', '+49 89 2222-200', NOW(), NOW()
);

INSERT INTO autohaus (
    version, name, anzahl_fahrzeuge, gruendungsdatum, homepage, telefonnummer, erzeugt, aktualisiert
) VALUES (
    0, 'BMW Zentrum Berlin', 3, '1998-11-10', 'https://www.bmw-berlin.de', '+49 30 9999-300', NOW(), NOW()
);

-- Adressen einfügen
INSERT INTO adresse (
    plz, ort, land, autohaus_id
) VALUES (
    '70174', 'Stuttgart', 'Deutschland', 1000
);

INSERT INTO adresse (
    plz, ort, land, autohaus_id
) VALUES (
    '80538', 'München', 'Deutschland', 1001
);

INSERT INTO adresse (
    plz, ort, land, autohaus_id
) VALUES (
    '10115', 'Berlin', 'Deutschland', 1002
);

-- Autos einfügen - Porsche Zentrum Stuttgart
INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'S-PO-911', 'Porsche', '911 GT3 RS', 2024, 1000
);

INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'S-PO-912', 'Porsche', '911 Turbo S', 2023, 1000
);

INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'S-PO-914', 'Porsche', 'Cayenne Turbo', 2023, 1000
);

-- Autos einfügen - Ferrari Europa München
INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'M-FE-812', 'Ferrari', '812 Supersport', 2024, 1001
);

INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'M-FE-458', 'Ferrari', '458 Italia', 2022, 1001
);

INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'M-FE-ff', 'Ferrari', 'FF', 2021, 1001
);

-- Autos einfügen - BMW Zentrum Berlin
INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'B-BM-440', 'BMW', 'M440i xDrive', 2024, 1002
);

INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'B-BM-M3', 'BMW', 'M3', 2023, 1002
);

INSERT INTO auto (
    kennzeichen, marke, modell, baujahr, autohaus_id
) VALUES (
    'B-BM-X5', 'BMW', 'X5 M', 2023, 1002
);
