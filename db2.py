# MYSQL ലുമായി പൈത്തൺ കണക്റ്റ് ചെയ്യുമ്പോൾ പ്രയോഗിക്കേണ്ട പ്രധാനപ്പെട്ട മെത്തേഡുകൾ ഏതാണ്?
# MYSQL ലുമായി പൈത്തൺ കണക്റ്റ് ചെയ്യുമ്പോൾ പ്രയോഗിക്കേണ്ട പ്രധാനപ്പെട്ട മെത്തേഡുകൾ താഴെപ്പറയുന്നവയാണ്:
# 1. connect(): MYSQL ഡേറ്റാബേസുമായി കണക്ഷൻ സ്ഥാപിക്കാൻ ഉപയോഗിക്കുന്നു.
# 2. cursor(): കണക്ഷൻ ഒബ്ജക്റ്റിൽ നിന്ന് കർസർ ഒബ്ജക്റ്റ് സൃഷ്ടിക്കാൻ ഉപയോഗിക്കുന്നു, ഇത് SQL കമാൻഡുകൾ എക്സിക്യൂട്ട് ചെയ്യാൻ സഹായിക്കുന്നു.
# 3. execute(): SQL കമാൻഡുകൾ എക്സിക്യൂട്ട് ചെയ്യാൻ ഉപയോഗിക്കുന്നു.
# 4. fetchone(): കർസർ ഒബ്ജക്റ്റിൽ നിന്ന് ഒരു റെക്കോർഡ് റിട്ടേൺ ചെയ്യാൻ ഉപയോഗിക്കുന്നു.
# 5. fetchall(): കർസർ ഒബ്ജക്റ്റിൽ നിന്ന് എല്ലാ റെക്കോർഡുകളും റിട്ടേൺ ചെയ്യാൻ ഉപയോഗിക്കുന്നു.
# 6. commit(): ഡേറ്റാബേസിൽ മാറ്റങ്ങൾ സേവ് ചെയ്യാൻ ഉപയോഗിക്കുന്നു.
# 7. rollback(): ഡേറ്റാബേസിൽ മാറ്റങ്ങൾ റിവേർട്ട് ചെയ്യാൻ ഉപയോഗിക്കുന്നു.
# 8. close(): കർസർ ഒബ്ജക്റ്റും കണക്ഷൻ ഒബ്ജക്റ്റും അടയ്ക്കാൻ ഉപയോഗിക്കുന്നു.

# ഒരു ചെറിയ ഉദാഹരണത്തിലൂടെ ഈ പറഞ്ഞ എല്ലാ മെത്തേഡ്സും കണിക്കുക:
import mysql.connector
from mysql.connector import Error
def connect_fetch():
    """ MYSQL ഡേറ്റാബേസുമായി കണക്റ്റ് ചെയ്ത് ഡാറ്റ ഫെച്ച് ചെയ്യുക """
    try:
        # connect() മെത്തേഡ് ഉപയോഗിച്ച് ഡേറ്റാബേസുമായി കണക്ഷൻ സ്ഥാപിക്കുക
        connection = mysql.connector.connect(
            host='localhost',
            database='Odayan',
            user='root',
            password=''
        )
        if connection.is_connected():
            print("Successfully connected to the database")

            # cursor() മെത്തേഡ് ഉപയോഗിച്ച് കർസർ ഒബ്ജക്റ്റ് സൃഷ്ടിക്കുക
            cursor = connection.cursor()

            # execute() മെത്തേഡ് ഉപയോഗിച്ച് SQL കമാൻഡ് എക്സിക്യൂട്ട് ചെയ്യുക
            cursor.execute("SELECT * FROM country_code")

            # fetchall() മെത്തേഡ് ഉപയോഗിച്ച് എല്ലാ റെക്കോർഡുകളും റിട്ടേൺ ചെയ്യുക
            records = cursor.fetchall()
            print("Total number of rows in table: ", cursor.rowcount)

            for row in records:
                print(row)

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        # close() മെത്തേഡ് ഉപയോഗിച്ച് കർസർ ഒബ്ജക്റ്റും കണക്ഷൻ ഒബ്ജക്റ്റും അടയ്ക്കുക
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
# ഫംഗ്ഷൻ വിളിക്കുക
connect_fetch()


# ഇതിൻ്റെ ഔട്ട്പുട്ട് ഇങ്ങനെ ആയിരിക്കും:
# Successfully connected to the database
# Successfully connected to the database
# Total number of rows in table:  245
# (1, 'DZD', 'Algerian Dinar', 'DZ', 'Algeria', '213', 'Africa')
# (2, 'AOA', 'Angolan Kwanza', 'AO', 'Angola', '244', 'Africa')
# (3, 'XOF', 'CFA Franc BCEAO', 'BJ', 'Benin', '229', 'Africa')
# .....
# (244, 'UYU', 'Uruguay Peso', 'UY', 'Uruguay', '598', 'South America')
# (245, 'VEF', 'Venezuela Bolivar', 'VE', 'Venezuela', '58', 'South America')
# MySQL connection is closed