# Pokemon GO IV calculator and database
## Usage

Thanks to [Nikita](https://github.com/nkouevda) for writing most of this code, I just made some additions

### First set executable
    chmod +x pgo

### calculate IVs
    python pgo.py calc [pokemon name] [CP] [Health] [Dust to power up] [phrase] [strongest feature] [perfect iv] -v

### Phrases
    - amazing
    - strong
    - decent
    - bad
    - all

### Strongest feature
    - atk
    - def
    - stam

### If pokemon has at least 1 perfect IV
    - wow

### Sample
    python pgo.py calc diglett 71 10 600 amazing def wow -v