-- Modify "receipts" table
ALTER TABLE "public"."receipts" ADD CONSTRAINT "receipts_order_id_key" UNIQUE ("order_id");
