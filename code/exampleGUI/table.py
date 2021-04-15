from browser import document, alert
from browser.html import TABLE, TR, TH, TD, INPUT

def insert_table(event):
    table = TABLE()

    # header row
    table <= TR(TH(f"Column {i}") for i in range(5))

	# read the text from a text field
    input = document["text"].value
    # table rows
    for row in range(6):
        inp = INPUT(type="number", step="0.01", id=f"text{row}", value=f"{row*2}")
        inp.bind("change", update_count)
        table <= TR(TD(f"{input}-{row}")+TD(f"Cell {row}")+TD(f"Cell {row}")+TD(f"Cell {row}")+TD(inp))
    table <= TR(TD("Total")+TD()+TD()+TD()+TD(type="number", id="total"))

	# set the text area content
    document["tableArea"].clear()
    document["tableArea"] <= table
    
    update_count(2)

def update_count(event):
    count = 0
    
    for row in range(6):
    	count = count + float(document[f"text{row}"].value)
    document["total"].textContent = f"{count:.2f}"

    
# bind the generation of the table to the button click
document["buttonUpdate"].bind("click", insert_table)

# generate the table on page load
insert_table(1)
