# Documentazione del progetto
#### Documentazione relativa al progetto di Reti di Telecomunicazioni sulla simulazione di un protocollo di routing in Python.
**Autore**: Francesco Tonelli, Matricola 0001071531

## Indice
1. [Introduzione](#introduzione)
2. [Requisiti](#requisiti)
3. [Avvio](#avvio)
4. [Utilizzo](#utilizzo)
5. [Struttura del Codice](#struttura-del-codice)

## Introduzione
La traccia del progetto indicava di sviluppare la simulazione di un protocollo di routing semplice. <br>
Ho optato per il protocollo di Distance Vector Routing, il quale però presenta limitazioni in caso di guasti nei collegamenti o nei nodi, poiché gli aggiornamenti delle routing table possono risultare errati in tali circostanze. <br>
Per superare questo limite, ho modificato l'algoritmo rendendolo più adattivo, così da garantire la continuità e la correttezza degli aggiornamenti anche in seguito ad una qualsiasi rimozione di un elemento della rete. <br>
Infine, ho implementato un'interfaccia grafica interattiva per permettere agli utenti di testare l'algoritmo su una rete personalizzata.

## Requisiti
- <b>Windows</b>: Python 3.9 o superiore
- <b>Linux/iOS</b>: Python 3.9
- <b>Connessione Internet</b>: al primo avvio, se non già presenti, dovranno essere scaricate le librerie *tkinter* (che mette a disposizione funzioni per creare interfacce grafiche) e *tabulate* (che genera tabelle testuali leggibili, utilizzate nella stampa delle routing tables dei nodi). Questo download viene eseguito automaticamente dagli script forniti per il running del progetto, che necessiteranno, quindi, di una connessione ad internet.

## Avvio
<b>Windows</b>: fare un doppio click sul file *start.bat* o, da linea di comando sulla root del progetto, lanciare `.\start.bat` <br>
<b>Linux/iOS</b>: aprire il terminale sulla root del progetto, digitare il comando `chmod 777 start.sh` e premere *Invio*, per consentire l'esecuzione dello script. Successivamente, fare un doppio click sul file *start.sh* o, da linea di comando, sempre sulla root, lanciare `./start.sh`

### Cosa succede all'avvio?
1. Entrambi gli script tenteranno, innanzitutto, di installare o aggiornare <b>pip</b>, per garantire i successivi download.
2. Se non già presenti, gli script scaricheranno, o aggiorneranno, le librerie necessarie sopracitate.
3. Se tutte le installazioni saranno andate a buon fine, gli script lanceranno l'applicazione.

## Utilizzo
All'avvio, l'applicazione si presenta come in figura, con una schermata bianca sulla sinistra e un menu sulla destra.

![GUI](./images/initial_gui.png)

Tramite questa interfaccia, è possibile:

- <b>Aggiungere un nodo</b> cliccando con il pulsante sinistro in un qualsiasi punto della schermata bianca. I nodi saranno inizializzati con un identificatore incrementale: il primo creato sarà il numero 1, il secondo il 2, e così via. <br>
<u>Nota</u>: l'identificativo di un nodo eliminato non viene riutilizzato per creare altri nodi.
- <b>Aggiungere un arco</b> compilando i tre campi nel menu a destra, inserendo gli identificativi dei due nodi interessati e il peso dell'arco, e premendo il pulsante "Add Edge". <br>
<u>Nota</u>: ogni arco è bidirezionale, non può avere ad entrambi gli estremi lo stesso nodo e non può esistere più di un arco fra i medesimi due nodi.
- <b>Eliminare un elemento</b> cliccando con il tasto destro vicino allo stesso. Verrà selezionato il nodo o l'arco che si trova più vicino al punto in cui si è cliccato. Si aprirà una finestra di dialogo, in cui si chiede conferma della cancellazione, e, in caso di risposta affermativa a quest'ultima, verrà cancellato l'elemento selezionato.
- <b>Stampare le routing tables dei nodi</b> tramite l'apposito pulsante in basso a destra. Verrà generato (o sovrascritto, se già presente) il file *RoutingTables.txt* nella root del progetto, il quale conterrà la routing table di ogni nodo e l'elenco degli archi fisici presenti nella rete, in formato testuale.

All'avvio dell'applicazione, inoltre, viene generato il file *log.txt* (contenente un log dettagliato di ogni evento), sempre nella root del progetto, che viene aggiornato ad ogni azione e ad ogni update dei nodi, per fornire un quadro più dettagliato di cosa sta succedendo durante l'esecuzione.

## Struttura del Codice
Il progetto si divide in due file, uno che gestisce la logica e uno che si occupa della grafica.
### DVR_view
### DVR_logic