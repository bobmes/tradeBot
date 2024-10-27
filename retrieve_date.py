from Historic_Crypto import Cryptocurrencies, HistoricalData

pairs_df = Cryptocurrencies().find_crypto_pairs()

#print(pairs_df[pairs_df['display_name'].str.contains('ADA/EUR')])

# adaEurData = HistoricalData('LINK-EUR',300,'2020-07-20-00-00').retrieve_data()
# adaEurData.to_csv('link_eur.csv')

# adaEurData = HistoricalData('MATIC-EUR',300,'2020-01-01-00-00').retrieve_data()
# adaEurData.to_csv('matic_eur.csv')


# adaEurData = HistoricalData('TRX-EUR',300,'2020-01-01-00-00').retrieve_data()
# adaEurData.to_csv('trx_eur.csv')

adaEurData = HistoricalData('LTC-EUR',300,'2020-01-01-00-00').retrieve_data()
adaEurData.to_csv('ltc_eur.csv')