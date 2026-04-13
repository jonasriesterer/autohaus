# GraphQL-Test mit Bruno

Diese GraphQL-Schnittstelle kann mit den Bruno-Tests aus `extras/bruno/patient/GraphQL` geprüft werden.

## Vorgehen

1. Anwendung starten
   - Stelle sicher, dass das Autohaus-Backend läuft.
   - Der Standard-Endpunkt wird in Bruno über `{{baseUrl}}/graphql` definiert.

2. Bruno-Collection öffnen
   - Importiere oder öffne die Collection aus `extras/bruno/patient/opencollection.yml`.
   - Alternativ kannst du direkt den Ordner `extras/bruno/patient/GraphQL` verwenden.

3. Basis-URL prüfen
   - In `extras/bruno/patient/opencollection.yml` ist `baseUrl` voreingestellt auf `https://127.0.0.1:8000`.
   - Passe `baseUrl` bei Bedarf an deine lokale Testumgebung an.

4. GraphQL-Queries ausführen
   - Die lesenden GraphQL-Tests liegen in `extras/bruno/patient/GraphQL/Query`.
   - Diese senden POST-Anfragen an `{{graphqlUrl}}`, wobei `graphqlUrl` in `extras/bruno/patient/GraphQL/folder.yml` als `{{baseUrl}}/graphql` definiert ist.

5. Nur Lese-Tests verwenden
   - Wenn du nur das Lesen von Daten testen möchtest, führe die Tests aus dem `Query`-Ordner aus.
   - `Login`- und `Mutation`-Tests sind separat und müssen nur bei Bedarf verwendet werden.

## Hinweise

- Die GraphQL-Abfragen verwenden `query`-Requests gegen den `/graphql`-Endpunkt.
- Für Leseoperationen ist kein zusätzlicher `Mutation`-Support erforderlich.
- Wenn die API über eine andere URL erreichbar ist, passe `baseUrl` und ggf. `graphqlUrl` in den Bruno-Variablen an.
