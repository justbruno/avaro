avaro is a lightweight and flexible cryptocurrency trading bot.

The purpose of the design is to enable experimentation with ease and flexibility. Key modules are fairly decoupled and can be reused or replaced with ease. Object-oriented constructs are used sparingly in order to avoid imposing unnecessary restrictions.

**Note** that avaro is a personal project developed for educational purposes, and it is in constant evolution. It comes with no guarantees, and some of the ambitions advertised above may not yet be fully realised.

# Features
- Modular design.
- Seamless exchange replacement.
- Strategies written in pure Python can be easily plugged in.
- Real-time parameter tuning.
- Simulation mode, in real or accelerated time to rapidly debug your strategies and optimize their parameters.

# Running the bot
You can run the bot with the following command:

`python launcher.py -c conf/simulation.conf`

Using a simulation configuration file is recommended at first, to familiarise yourself with the bot.

# Strats
Strategies are divided into buy and sell decisions, implemented in separate modules. avaro is designed so that strats only need to decide when it is a good time to buy/sell (although they can also decide trade price and volume). When that happens, the strategy only needs to generate an event (see callbacks in `orchestrator.py` and the example strategies). avaro takes care of communicating with the exchange and recording successful trades.

## Example strat
An example of how to write your own strat is given in `strats/simple_ema.py`, with configuration file `conf/simple_ema.conf`.

# Simulation mode
The simulation mode is designed to be frictionless. The only script that is aware that we are running a simulation is the launcher. All others (except dummy replacements) run exactly the same. In order to run in simulation mode, you just need to replace the exchange interface (and optionally the order book monitor) with the corresponding simulation module.

## Simulation example

For normal operation (using a real interface to Kraken), you would set the following values in the input configuration file:

    EXCHANGE='kraken_interface' <br/>
    BOOK='kraken_book' <br/>
    BOOK_PARAMS={} <br/>
    ASSETS_FILE='assets.txt' <br/>
    LOGS_DIR='logs/' <br/>

For a simulation, you may instead use

    EXCHANGE='dummy_exchange' <br/>
    BOOK='manual_dummy_book' <br/>
    BOOK_PARAMS={'book_input':'manual_input_file.txt'} <br/>
    ASSETS_FILE='dummy_assets.txt' <br/>
    LOGS_DIR='dummy_logs/' <br/>

or

    EXCHANGE='dummy_exchange' <br/>
    BOOK='dump_dummy_book' <br/>
    BOOK_PARAMS={'book_input':'kraken_book_dump.txt'} <br/>
    ASSETS_FILE='dummy_assets.txt' <br/>
    LOGS_DIR='dummy_logs/' <br/>

**Warning**: When running a simulation, make sure you change the `ASSETS_FILE` and `LOGS_DIR` to avoid interfering with your data.

You can also change parameters such as `SPEEDUP`, to change the speed of the simulation (e.g. SPEEDUP=10 accelerates the simulation by a factor of 10). Since the strats and the book monitor run on separate threads, the simulation may not be entirely consistent at different speeds. `exchange/dump_dummy_book.py` has a sync parameter to help alleviate this, but note that the strats need to register a condition at the end of each iteration (see `strats/dip_chaser.py` and `strats/rally_chaser.py` for an example).

Check the file `conf/simulation.conf` for an example of a configuration file set up for simulation.

# Exchanges

avaro is decoupled from the exchange being used. An interface for Kraken is included (`exchange/kraken_interface.py`, `exchange/kraken_book.py`), but this can be replaced with a suitably written interface for your favourite exchange.

If using the provided Kraken interface, make sure you specify the location of your API keys in `exchange/kraken_interface.py`.

# Examples of reusability
To illustrate the reusable nature of some of the modules, some examples are included, such as
- `collect_book_data.py`, to collect order book data dumps;
- `interactive_trader.py`, a simplistic command-line interface interactive trader.

# Asset management
avaro includes a simple asset manager to help you keep track of the assets you currently hold. Profits made while an asset has been held are tracked, so that you can decide whether to sell it at a loss without incurring a loss overall.

# Dependencies

The Kraken interface depends on
https://github.com/krakenfx/kraken-wsclient-py

# Disclaimer

Use this software at your own risk. The author assumes no responsibility for your trading results.

