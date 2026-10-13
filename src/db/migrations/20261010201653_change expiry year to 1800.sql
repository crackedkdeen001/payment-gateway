-- Modify "receipts" table
ALTER TABLE "public"."receipts" DROP CONSTRAINT "receipts_card_expiry_year_check", ADD CONSTRAINT "receipts_card_expiry_year_check" CHECK (card_expiry_year >= 1800);
-- Modify "receipts_audit" table
ALTER TABLE "public"."receipts_audit" DROP CONSTRAINT "receipts_audit_card_expiry_year_check", ADD CONSTRAINT "receipts_audit_card_expiry_year_check" CHECK (card_expiry_year >= 1800);
