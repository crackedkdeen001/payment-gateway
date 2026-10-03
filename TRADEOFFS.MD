- if the bank a card is authorized by the bank but it reports expires, we will delete the records
- we can also blacklist it
- No update column in the idempotency table as idempotency keys are one time use

todo 
- updated at column in receipt in case of card changes
- use authorize, capture, refund column for explicitly of reference at the exchange of space
- cents is integer not decimal as it is the lowest denomination of money in the USA
- debated having a receipt_id field in the idempotency table for getting seen requests but, the request to the /auth endpoint doesn't have a receipt yet.

# Todo 
Change test code to reflect no trigger on bank ref time change