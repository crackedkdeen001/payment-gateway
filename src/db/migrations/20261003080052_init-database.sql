-- Create enum type "payment_states"
CREATE TYPE "public"."payment_states" AS ENUM ('pending', 'authorized', 'captured', 'voided', 'refunded');
-- Create "idempotency_keys" table
CREATE TABLE "public"."idempotency_keys" (
  "id" serial NOT NULL,
  "idempotency_key" character varying(100) NOT NULL,
  "request_path" character varying(100) NOT NULL,
  "request_body" jsonb NOT NULL,
  "response_body" jsonb NULL,
  "response_code" integer NULL,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id")
);
-- Create index "idempotency_key_request_path_idx" to table: "idempotency_keys"
CREATE UNIQUE INDEX "idempotency_key_request_path_idx" ON "public"."idempotency_keys" ("idempotency_key", "request_path");
-- Create "receipts" table
CREATE TABLE "public"."receipts" (
  "id" serial NOT NULL,
  "order_id" uuid NOT NULL,
  "customer_id" integer NOT NULL,
  "amount_in_cents" integer NOT NULL,
  "currency" character varying(3) NOT NULL,
  "card_number" character varying(100) NOT NULL,
  "card_cvv" character varying(3) NOT NULL,
  "card_expiry_month" integer NOT NULL,
  "card_expiry_year" integer NOT NULL,
  "current_state" "public"."payment_states" NOT NULL DEFAULT 'pending',
  "authorize_id" character varying(100) NULL,
  "authorized_at" timestamp NULL,
  "auth_expiry" timestamp NULL,
  "capture_id" character varying(100) NULL,
  "captured_at" timestamp NULL,
  "void_id" character varying(100) NULL,
  "voided_at" timestamp NULL,
  "refund_id" character varying(100) NULL,
  "refunded_at" timestamp NULL,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("id"),
  CONSTRAINT "receipts_card_expiry_month_check" CHECK ((card_expiry_month >= 1) AND (card_expiry_month <= 12)),
  CONSTRAINT "receipts_card_expiry_year_check" CHECK (card_expiry_year >= 1)
);
-- Create index "receipts_customer_id_idx" to table: "receipts"
CREATE INDEX "receipts_customer_id_idx" ON "public"."receipts" ("customer_id");
-- Create index "receipts_order_id_idx" to table: "receipts"
CREATE INDEX "receipts_order_id_idx" ON "public"."receipts" ("order_id");
-- Create "receipts_audit" table
CREATE TABLE "public"."receipts_audit" (
  "receipt_id" integer NOT NULL,
  "order_id" uuid NOT NULL,
  "customer_id" integer NOT NULL,
  "amount_in_cents" integer NOT NULL,
  "currency" character varying(3) NOT NULL,
  "card_number" character varying(100) NOT NULL,
  "card_cvv" character varying(3) NOT NULL,
  "card_expiry_month" integer NOT NULL,
  "card_expiry_year" integer NOT NULL,
  "current_state" "public"."payment_states" NOT NULL DEFAULT 'pending',
  "authorize_id" character varying(100) NULL,
  "authorized_at" timestamp NULL,
  "capture_id" character varying(100) NULL,
  "captured_at" timestamp NULL,
  "void_id" character varying(100) NULL,
  "voided_at" timestamp NULL,
  "refund_id" character varying(100) NULL,
  "refunded_at" timestamp NULL,
  "action" text NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT "receipts_audit_action_check" CHECK (action = ANY (ARRAY['del'::text, 'upd'::text, 'ins'::text])),
  CONSTRAINT "receipts_audit_card_expiry_month_check" CHECK ((card_expiry_month >= 1) AND (card_expiry_month <= 12)),
  CONSTRAINT "receipts_audit_card_expiry_year_check" CHECK (card_expiry_year >= 1)
);
