import uuid
import random
from datetime import datetime, timedelta, timezone

# Configuration
TENANT_1 = "56f292e4-80f1-704a-38f4-42f883cf5d91"
TENANT_2 = "5692b244-30d1-7072-584e-1b3637f04ab7"

GOOD_USER = "good_user_01"
BAD_USER = "bad_user_01"

now = datetime.now(timezone.utc)

sql_statements = []

# --- 1. CLEAR DATABASES ---
sql_statements.append("\\connect aegis_transactions;")
sql_statements.append("TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;")

sql_statements.append("\\connect aegis_risk;")
sql_statements.append("TRUNCATE TABLE account_profiles RESTART IDENTITY CASCADE;")
sql_statements.append("TRUNCATE TABLE risk_results RESTART IDENTITY CASCADE;")


# --- 2. GENERATE GOOD USER TRANSACTIONS ---
sql_statements.append("\\connect aegis_transactions;")

good_txns = []
good_start_date = now - timedelta(days=180)

# 1 transaction every ~3 days
current_date = good_start_date
total_good_volume = 0.0

while current_date < now:
    # Established users do bigger transactions
    amount = round(random.uniform(500.0, 2500.0), 2)
    total_good_volume += amount
    txn_id = str(uuid.uuid4())
    good_txns.append(txn_id)
    
    sql = f"""
    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '{txn_id}', 'idemp_good_{txn_id}', {amount}, 'GBP', '{GOOD_USER}', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '{current_date.isoformat()}', '{TENANT_1}', 'PAYMENT'
    );
    """
    sql_statements.append(sql)
    current_date += timedelta(days=random.uniform(2, 5))

# --- 3. GENERATE BAD USER TRANSACTIONS ---
bad_txns = []
bad_start_date = now - timedelta(days=2) # Only 2 days ago!
current_date = bad_start_date
total_bad_volume = 0.0

# 15 high-velocity transactions
countries = ['RU', 'NG', 'US', 'GB', 'CN']
devices = ['device_bad_1', 'device_bad_2', 'device_bad_3', 'device_bad_4']

for i in range(15):
    amount = round(random.uniform(1000.0, 5000.0), 2)
    total_bad_volume += amount
    txn_id = str(uuid.uuid4())
    bad_txns.append(txn_id)
    
    sender_country = random.choice(countries)
    device = random.choice(devices)
    
    sql = f"""
    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '{txn_id}', 'idemp_bad_{txn_id}', {amount}, 'USD', '{BAD_USER}', 'unknown_crypto_exchange', 
        '{sender_country}', 'CY', '{device}', '10.0.{random.randint(1,255)}.{random.randint(1,255)}', 'api', 
        'COMPLETED', '{current_date.isoformat()}', '{TENANT_2}', 'CRYPTO_PURCHASE'
    );
    """
    sql_statements.append(sql)
    current_date += timedelta(hours=random.uniform(0.5, 3))


# --- 4. GENERATE RISK PROFILES ---
sql_statements.append("\\connect aegis_risk;")

# Good User Profile
good_profile = f"""
INSERT INTO account_profiles (
    account_id, total_txn_count, total_volume_lifetime, total_volume_30d, txn_count_30d, 
    total_volume_24h, txn_count_24h, txn_count_1h, total_volume_1h, avg_txn_amount, 
    max_txn_amount, is_high_risk, fraud_txn_count, blocked_txn_count, review_txn_count, 
    unique_receiver_count, known_receiver_ids, unique_device_count, known_device_fingerprints, 
    unique_country_count, known_receiver_countries, first_seen_at, last_seen_at, version
) VALUES (
    '{GOOD_USER}', {len(good_txns)}, {total_good_volume}, {total_good_volume * 0.15}, 10, 
    0, 0, 0, 0, {total_good_volume/len(good_txns)}, 
    5000.00, false, 0, 0, 0, 
    5, ARRAY['merchant_trusted', 'merchant_1', 'merchant_2', 'merchant_3', 'merchant_4'], 1, ARRAY['device_good_1'], 
    1, ARRAY['GB'], '{good_start_date.isoformat()}', '{(now - timedelta(days=1)).isoformat()}', 1
);
"""
sql_statements.append(good_profile)

# Bad User Profile
bad_profile = f"""
INSERT INTO account_profiles (
    account_id, total_txn_count, total_volume_lifetime, total_volume_30d, txn_count_30d, 
    total_volume_24h, txn_count_24h, txn_count_1h, total_volume_1h, avg_txn_amount, 
    max_txn_amount, is_high_risk, fraud_txn_count, blocked_txn_count, review_txn_count, 
    unique_receiver_count, known_receiver_ids, unique_device_count, known_device_fingerprints, 
    unique_country_count, known_receiver_countries, first_seen_at, last_seen_at, version
) VALUES (
    '{BAD_USER}', {len(bad_txns)}, {total_bad_volume}, {total_bad_volume}, 15, 
    {total_bad_volume}, 15, 5, 10000.00, {total_bad_volume/len(bad_txns)}, 
    5000.00, true, 2, 5, 8, 
    1, ARRAY['unknown_crypto_exchange'], 4, ARRAY['device_bad_1', 'device_bad_2', 'device_bad_3', 'device_bad_4'], 
    5, ARRAY['RU', 'NG', 'US', 'GB', 'CN'], '{bad_start_date.isoformat()}', '{now.isoformat()}', 15
);
"""
sql_statements.append(bad_profile)

# Write to file
with open("c:\\Users\\USER\\Documents\\aegis-risk\\seed_data.sql", "w") as f:
    f.write("\n".join(sql_statements))

print("seed_data.sql generated successfully.")
