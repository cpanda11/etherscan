from bitforex.models import Account

account_file = open('accounts.txt')
accounts = account_file.readlines()
account_file.close()

email_password = ''
bitforex_password = ''
results = []
for account in accounts:
    account = account.strip().split('\t')
    if 3 == len(account):
        email_password = account[1]
        bitforex_password = account[2]
        results.append([account[0], account[1], account[2]])
    elif 2 == len(account):
        results.append([account[0], account[1], bitforex_password])
    elif 1 == len(account):
        results.append([account[0], email_password, bitforex_password])

for result in results:
    a = Account(email=result[0], email_password=result[1], bitforex_password=result[2])
    a.save()

print(len(accounts))
