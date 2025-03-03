# quantify ur losses from robinhood

<img width="816" alt="image" src="https://github.com/user-attachments/assets/161f0a9b-26fa-4f61-96b1-fec256f6f72f" />

### how it works

1. scans for your data
2. [function] extracts transaction info
3. [function] fetches current spy price
4. [function] saves transaction to supabase, and # of spy shares that could have been purchased
5. [function] calculates the new value of the portfolio, and how much you could have made if you just bought spy
6. [function] sends an update email. probably with negative alpha.
