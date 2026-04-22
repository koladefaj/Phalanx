\connect aegis_transactions;
TRUNCATE TABLE transactions RESTART IDENTITY CASCADE;
\connect aegis_risk;
TRUNCATE TABLE account_profiles RESTART IDENTITY CASCADE;
TRUNCATE TABLE risk_results RESTART IDENTITY CASCADE;
\connect aegis_transactions;

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'dd5ef6de-c6b0-4542-b8bc-82257d5cba46', 'idemp_good_dd5ef6de-c6b0-4542-b8bc-82257d5cba46', 1343.47, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-10-24T22:13:05.817710+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '051d5602-7bf8-49e7-825c-1a2df6d986d8', 'idemp_good_051d5602-7bf8-49e7-825c-1a2df6d986d8', 756.1, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-10-28T20:58:04.584549+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'f86994d0-6c11-466d-a04b-800f006bbe7d', 'idemp_good_f86994d0-6c11-466d-a04b-800f006bbe7d', 1298.8, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-10-31T12:44:49.287954+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'cbec25c1-9955-458a-9437-cdbc1ad98924', 'idemp_good_cbec25c1-9955-458a-9437-cdbc1ad98924', 1832.2, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-04T11:31:37.368535+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '02b2572a-8f96-4ded-a124-f4495bde52c0', 'idemp_good_02b2572a-8f96-4ded-a124-f4495bde52c0', 681.65, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-07T17:04:48.370480+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '17c92e75-f947-433d-bdc5-beb05bb0e0dd', 'idemp_good_17c92e75-f947-433d-bdc5-beb05bb0e0dd', 2284.69, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-09T17:39:12.979984+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd0edea20-613b-4aeb-9a30-c9701a7a8a14', 'idemp_good_d0edea20-613b-4aeb-9a30-c9701a7a8a14', 2117.03, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-13T20:35:33.816418+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '1cadbd46-12e7-4066-924a-c1417c1f7619', 'idemp_good_1cadbd46-12e7-4066-924a-c1417c1f7619', 2022.43, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-16T10:14:53.826014+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '7b34304c-fd15-4d8c-a1d5-87d84b94f0a6', 'idemp_good_7b34304c-fd15-4d8c-a1d5-87d84b94f0a6', 1468.87, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-20T21:27:12.634526+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'eaafdc1d-e4ac-4630-b5ca-c926be2f5ab8', 'idemp_good_eaafdc1d-e4ac-4630-b5ca-c926be2f5ab8', 1300.62, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-23T16:54:02.560058+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '80705785-b644-4a7c-9395-740a17eecd1d', 'idemp_good_80705785-b644-4a7c-9395-740a17eecd1d', 823.45, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-27T01:24:25.259485+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'b5dd326d-9628-4b94-8709-4bb467b063c2', 'idemp_good_b5dd326d-9628-4b94-8709-4bb467b063c2', 2223.41, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-11-29T14:45:34.717458+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'e3bb5265-96c6-4296-93b3-17db54b36369', 'idemp_good_e3bb5265-96c6-4296-93b3-17db54b36369', 999.61, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-01T19:14:05.022185+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2a8bf5f3-1a96-4fa1-b5d1-ba3e5c53592c', 'idemp_good_2a8bf5f3-1a96-4fa1-b5d1-ba3e5c53592c', 2130.73, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-04T01:30:27.087525+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '5cee1e09-d5dc-4fb0-abc2-4a148ad4cf57', 'idemp_good_5cee1e09-d5dc-4fb0-abc2-4a148ad4cf57', 719.72, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-06T13:09:10.462534+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '0f8b67a3-15f4-45f0-b1bb-a32b687c58aa', 'idemp_good_0f8b67a3-15f4-45f0-b1bb-a32b687c58aa', 760.18, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-11T11:07:44.103972+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '0b6a8d1d-b135-43c3-8cac-d6e7b8342c4f', 'idemp_good_0b6a8d1d-b135-43c3-8cac-d6e7b8342c4f', 2283.74, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-13T16:20:45.735502+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '3cd3b10b-01b7-4cc9-8229-3fc3ffb57563', 'idemp_good_3cd3b10b-01b7-4cc9-8229-3fc3ffb57563', 995.3, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-18T00:02:33.293462+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'cd0bcf57-5eeb-41de-9ccd-de2c476f726d', 'idemp_good_cd0bcf57-5eeb-41de-9ccd-de2c476f726d', 1083.96, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-22T08:26:43.090288+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '095e2f38-8a69-418c-9740-2926b9c97233', 'idemp_good_095e2f38-8a69-418c-9740-2926b9c97233', 2360.75, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-27T05:45:15.230971+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd82d8011-d133-4a0c-ba8f-81b4780b9b21', 'idemp_good_d82d8011-d133-4a0c-ba8f-81b4780b9b21', 1676.95, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-31T10:05:20.326349+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'be40bb84-ef57-49f9-bd94-8d1fe1ae1922', 'idemp_good_be40bb84-ef57-49f9-bd94-8d1fe1ae1922', 1763.65, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-04T20:18:41.805775+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'ed3606a8-b96d-4157-9f7e-8d07d61b6127', 'idemp_good_ed3606a8-b96d-4157-9f7e-8d07d61b6127', 935.79, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-07T03:46:15.404448+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'e42d90a3-f99c-4e9d-b775-e00211541af2', 'idemp_good_e42d90a3-f99c-4e9d-b775-e00211541af2', 2359.73, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-09T08:10:46.292263+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'f2454ed4-bc19-48e7-9480-4d85ea7e53d4', 'idemp_good_f2454ed4-bc19-48e7-9480-4d85ea7e53d4', 717.77, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-12T15:14:21.119346+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '429a211d-f762-44a2-a824-71e593ce87b0', 'idemp_good_429a211d-f762-44a2-a824-71e593ce87b0', 1180.79, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-16T19:27:20.052630+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'b6bead0c-cf1e-486a-924f-9d997f10cdcf', 'idemp_good_b6bead0c-cf1e-486a-924f-9d997f10cdcf', 1649.74, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-20T11:41:40.639516+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2393c01f-20ce-45ba-a88b-a17de7f01d69', 'idemp_good_2393c01f-20ce-45ba-a88b-a17de7f01d69', 1598.32, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-24T13:24:55.500305+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '94b60215-a44c-4712-a88d-7d2891f4d72b', 'idemp_good_94b60215-a44c-4712-a88d-7d2891f4d72b', 1081.67, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-27T01:30:29.707602+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '14121b7e-9a6c-4b38-9884-090d4cb909a4', 'idemp_good_14121b7e-9a6c-4b38-9884-090d4cb909a4', 2112.1, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-29T05:21:22.832799+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'aaf0e5e9-df38-431b-9401-13496cb55f1f', 'idemp_good_aaf0e5e9-df38-431b-9401-13496cb55f1f', 624.96, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-31T20:09:27.625327+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '0331e63a-8b81-476a-8ac3-39668044977b', 'idemp_good_0331e63a-8b81-476a-8ac3-39668044977b', 2233.33, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-04T23:49:03.565298+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'e3ef5370-8310-4431-8c0c-f2fc35f94839', 'idemp_good_e3ef5370-8310-4431-8c0c-f2fc35f94839', 1076.76, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-07T21:37:20.509367+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '35bbb34c-8ec9-42fd-8cda-7c51b8dbd047', 'idemp_good_35bbb34c-8ec9-42fd-8cda-7c51b8dbd047', 1329.37, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-10T02:20:10.600478+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2d729ca4-4182-47a1-a2c2-a123b26366ae', 'idemp_good_2d729ca4-4182-47a1-a2c2-a123b26366ae', 1651.93, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-14T12:06:10.437176+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2bb17094-7ecc-4d26-a124-b651465c4dee', 'idemp_good_2bb17094-7ecc-4d26-a124-b651465c4dee', 2378.71, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-17T04:02:39.724392+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '7d202f31-c290-4689-a11e-6344c66194dc', 'idemp_good_7d202f31-c290-4689-a11e-6344c66194dc', 1530.59, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-22T02:33:51.216425+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'fd578d7a-a2a3-43d6-9b0c-aae814f6f924', 'idemp_good_fd578d7a-a2a3-43d6-9b0c-aae814f6f924', 825.27, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-24T05:01:17.734773+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6c03a03d-4a61-4311-8078-8968d1cfcba4', 'idemp_good_6c03a03d-4a61-4311-8078-8968d1cfcba4', 1043.05, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-28T12:27:04.703941+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '21fea940-3fb1-4303-97f6-0230458a4572', 'idemp_good_21fea940-3fb1-4303-97f6-0230458a4572', 669.41, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-02T18:55:38.891078+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '4070961c-9f01-4834-8041-b671c4f85ee2', 'idemp_good_4070961c-9f01-4834-8041-b671c4f85ee2', 852.49, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-05T15:17:11.740115+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '4c01e8a5-c13b-447a-89bd-09dae9ef273a', 'idemp_good_4c01e8a5-c13b-447a-89bd-09dae9ef273a', 1184.77, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-08T04:05:31.318462+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '42983ae4-b52d-4999-adf9-1d542893d1ef', 'idemp_good_42983ae4-b52d-4999-adf9-1d542893d1ef', 1211.23, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-12T18:39:56.582131+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'f35b2b8a-7440-4dff-bfde-c66b4fcd7386', 'idemp_good_f35b2b8a-7440-4dff-bfde-c66b4fcd7386', 1669.12, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-16T12:42:28.414810+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'b4ba5161-c305-441b-a789-2f2011fb3921', 'idemp_good_b4ba5161-c305-441b-a789-2f2011fb3921', 1993.28, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-20T13:34:22.861721+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '058b0381-9e2f-4a0d-af4f-f044f1a9b01d', 'idemp_good_058b0381-9e2f-4a0d-af4f-f044f1a9b01d', 1854.48, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-24T15:19:36.325071+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'e9a5282d-a3ef-476c-a7cf-863ac311148b', 'idemp_good_e9a5282d-a3ef-476c-a7cf-863ac311148b', 2476.98, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-28T18:05:01.488608+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'b27aa081-97f0-4abb-baf6-8f236e2fbe8f', 'idemp_good_b27aa081-97f0-4abb-baf6-8f236e2fbe8f', 526.38, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-02T11:21:00.987711+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '70536d7a-7e30-4ef1-9302-00ef9ef2b2c1', 'idemp_good_70536d7a-7e30-4ef1-9302-00ef9ef2b2c1', 703.09, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-04T16:27:01.818069+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'ddc3bfd5-0bb0-4082-8456-9b1e25e32470', 'idemp_good_ddc3bfd5-0bb0-4082-8456-9b1e25e32470', 1197.03, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-09T09:27:55.451791+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '9bc20636-b0f5-4083-94be-b05379d29f55', 'idemp_good_9bc20636-b0f5-4083-94be-b05379d29f55', 1400.32, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-14T06:21:44.005970+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'db945165-89c7-4592-ab42-3c71370e4468', 'idemp_good_db945165-89c7-4592-ab42-3c71370e4468', 1498.0, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-17T13:51:19.126851+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd9a9d0c7-4166-4211-b5c7-0aa3be7951d6', 'idemp_good_d9a9d0c7-4166-4211-b5c7-0aa3be7951d6', 1591.28, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-19T15:57:39.454382+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '0e55fdb3-70ff-4933-82a3-66c5a9b08cc2', 'idemp_good_0e55fdb3-70ff-4933-82a3-66c5a9b08cc2', 2132.06, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-21T18:18:01.075701+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'cc134e03-57c6-4d13-80cf-efabbd01ef50', 'idemp_bad_cc134e03-57c6-4d13-80cf-efabbd01ef50', 2653.32, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_1', '10.0.236.216', 'api', 
        'COMPLETED', '2026-04-20T22:13:05.817710+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'bda4ee41-a463-4bf1-8402-7a057e0464fb', 'idemp_bad_bda4ee41-a463-4bf1-8402-7a057e0464fb', 3247.77, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.168.89', 'api', 
        'COMPLETED', '2026-04-21T00:16:45.860351+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'fd3797cc-6c7d-4f41-9a2b-4d3970384649', 'idemp_bad_fd3797cc-6c7d-4f41-9a2b-4d3970384649', 2923.66, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.40.13', 'api', 
        'COMPLETED', '2026-04-21T02:15:39.127842+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'af54e674-c07e-4040-b4d6-6f0d87c9728e', 'idemp_bad_af54e674-c07e-4040-b4d6-6f0d87c9728e', 4944.77, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'GB', 'CY', 'device_bad_3', '10.0.82.181', 'api', 
        'COMPLETED', '2026-04-21T03:35:42.601231+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6e5a0dea-6dea-4273-9ef4-296bf6ce8988', 'idemp_bad_6e5a0dea-6dea-4273-9ef4-296bf6ce8988', 2731.64, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_4', '10.0.138.63', 'api', 
        'COMPLETED', '2026-04-21T06:06:02.574725+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'dd4a6b6b-f1bd-42c2-b6e6-0f0a174b1be7', 'idemp_bad_dd4a6b6b-f1bd-42c2-b6e6-0f0a174b1be7', 3181.73, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_3', '10.0.135.131', 'api', 
        'COMPLETED', '2026-04-21T08:57:47.439754+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '130d9741-b2b2-4947-93c0-114fb43c5017', 'idemp_bad_130d9741-b2b2-4947-93c0-114fb43c5017', 3698.47, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'GB', 'CY', 'device_bad_1', '10.0.207.150', 'api', 
        'COMPLETED', '2026-04-21T09:38:23.007660+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '3942bd42-5326-4946-a520-47ade6eddb0d', 'idemp_bad_3942bd42-5326-4946-a520-47ade6eddb0d', 1671.69, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'US', 'CY', 'device_bad_3', '10.0.61.31', 'api', 
        'COMPLETED', '2026-04-21T10:35:49.428321+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '15670e29-6ace-4c93-b20d-e6ea7e1237cb', 'idemp_bad_15670e29-6ace-4c93-b20d-e6ea7e1237cb', 2870.35, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_1', '10.0.247.28', 'api', 
        'COMPLETED', '2026-04-21T12:53:58.333065+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '28de76df-7ed6-42d7-87df-8239bb256c5f', 'idemp_bad_28de76df-7ed6-42d7-87df-8239bb256c5f', 2095.1, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.49.85', 'api', 
        'COMPLETED', '2026-04-21T15:46:58.614266+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'caf55c87-d414-43b1-8470-119d41e8f84f', 'idemp_bad_caf55c87-d414-43b1-8470-119d41e8f84f', 2829.81, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'US', 'CY', 'device_bad_2', '10.0.172.234', 'api', 
        'COMPLETED', '2026-04-21T16:20:03.058883+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'cf58faa2-4754-42a4-9ce0-15119ece8a34', 'idemp_bad_cf58faa2-4754-42a4-9ce0-15119ece8a34', 4300.73, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.186.231', 'api', 
        'COMPLETED', '2026-04-21T17:50:01.756340+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'a54a08f5-8fc6-481b-b95c-1f42a22c7715', 'idemp_bad_a54a08f5-8fc6-481b-b95c-1f42a22c7715', 3649.66, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'NG', 'CY', 'device_bad_1', '10.0.223.231', 'api', 
        'COMPLETED', '2026-04-21T18:30:05.315613+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6413a9c2-85f6-49d0-ae93-32252de6a82d', 'idemp_bad_6413a9c2-85f6-49d0-ae93-32252de6a82d', 1456.39, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_2', '10.0.155.113', 'api', 
        'COMPLETED', '2026-04-21T20:26:55.784318+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '71ae4e1b-fae7-4037-bfd5-a7dd4bf27e6b', 'idemp_bad_71ae4e1b-fae7-4037-bfd5-a7dd4bf27e6b', 2035.39, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.24.200', 'api', 
        'COMPLETED', '2026-04-21T23:04:01.899167+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    
\connect aegis_risk;

INSERT INTO account_profiles (
    account_id, total_txn_count, total_volume_lifetime, total_volume_30d, txn_count_30d, 
    total_volume_24h, txn_count_24h, txn_count_1h, total_volume_1h, avg_txn_amount, 
    max_txn_amount, is_high_risk, fraud_txn_count, blocked_txn_count, review_txn_count, 
    unique_receiver_count, known_receiver_ids, unique_device_count, known_device_fingerprints, 
    unique_country_count, known_receiver_countries, first_seen_at, last_seen_at, version
) VALUES (
    'good_user_01', 54, 78217.11, 11732.566499999999, 10, 
    0, 0, 0, 0, 1448.465, 
    5000.00, false, 0, 0, 0, 
    5, ARRAY['merchant_trusted', 'merchant_1', 'merchant_2', 'merchant_3', 'merchant_4'], 1, ARRAY['device_good_1'], 
    1, ARRAY['GB'], '2025-10-24T22:13:05.817710+00:00', '2026-04-21T22:13:05.817710+00:00', 1
);


INSERT INTO account_profiles (
    account_id, total_txn_count, total_volume_lifetime, total_volume_30d, txn_count_30d, 
    total_volume_24h, txn_count_24h, txn_count_1h, total_volume_1h, avg_txn_amount, 
    max_txn_amount, is_high_risk, fraud_txn_count, blocked_txn_count, review_txn_count, 
    unique_receiver_count, known_receiver_ids, unique_device_count, known_device_fingerprints, 
    unique_country_count, known_receiver_countries, first_seen_at, last_seen_at, version
) VALUES (
    'bad_user_01', 15, 44290.479999999996, 44290.479999999996, 15, 
    44290.479999999996, 15, 5, 10000.00, 2952.698666666666, 
    5000.00, true, 2, 5, 8, 
    1, ARRAY['unknown_crypto_exchange'], 4, ARRAY['device_bad_1', 'device_bad_2', 'device_bad_3', 'device_bad_4'], 
    5, ARRAY['RU', 'NG', 'US', 'GB', 'CN'], '2026-04-20T22:13:05.817710+00:00', '2026-04-22T22:13:05.817710+00:00', 15
);
