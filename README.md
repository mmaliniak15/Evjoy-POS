# Evjoy-POS
Please visit my amazing girlfiend's bakery [website](https://www.tasteevjoy.com/) for some delicious treats!

App was created using tkinter. 
Features:
* Customizable inventory: use "Inventory.csv" to update available items and pricing
* Cash and Credit pricing: custom pricing based on payment method. User can edit calc_total function in pos_source.py to customize how the total amount is calculated based on the payment method 
* Purchase History: all submitted orders will be recorded with items, price and timestamp

There are 2 options to use this:
1. Use src/pos_source.py directly
    * User will need to have python and requirement packages installed on their machine
2. Create a *.exe application using [pyinstaller](https://pyinstaller.org/en/stable/) of the python script
    * User can simply run the application without installer python or any packages
    * Made sure the 'Inventory.csv' and 'Purchase_History.csv' are located in the same folder and the application