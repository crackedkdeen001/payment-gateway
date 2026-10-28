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

- Changed state machine and idempotency Middleware to a single class housing both so only one connection is used per request instead of 2.
- Switched the Idempotency layer and state machine order. The tradeoff involved is that receipts trigger the idempotency layer even though the transition may be wrong but the way the cached results are fetched (key + request path) prevents it from returning a result as a key can only be used once per path.
- This also allows us to return cached responses in an easier fashion, as with the state machine first, we'd have allow a captured receipt on the /capture endpoint bypass to the idempotency layer to return the saved response.
- But this doesn't guarantee it as if the response isn't returned due to let's say the process dying before hand and response was saved. Since the caller can't use the same key per request, he'd have a
- Phases in each request are wrapped in a transaction to ensure that the operation is either committed or it fails, no in between