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
        'dd5abf0c-0d4d-4de8-8ad9-dfaa86bdae13', 'idemp_good_dd5abf0c-0d4d-4de8-8ad9-dfaa86bdae13', 2021.44, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-09T00:47:20.028682+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'fcc8da34-ad34-402b-967d-88904816b054', 'idemp_good_fcc8da34-ad34-402b-967d-88904816b054', 712.76, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-11T15:00:45.750868+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '1d82d0ef-3e2b-43c5-b899-68c4e08e29b0', 'idemp_good_1d82d0ef-3e2b-43c5-b899-68c4e08e29b0', 848.28, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-15T10:55:06.265996+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '3977a1d6-f315-4877-b59a-3e461f117e40', 'idemp_good_3977a1d6-f315-4877-b59a-3e461f117e40', 1112.6, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-18T10:19:46.929842+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '08e7d488-fefe-425e-b443-41b3d5d8ccd4', 'idemp_good_08e7d488-fefe-425e-b443-41b3d5d8ccd4', 1824.52, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-20T23:03:02.710083+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '424164c2-c3fd-4000-838d-88a1bb0fce56', 'idemp_good_424164c2-c3fd-4000-838d-88a1bb0fce56', 1448.15, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-23T10:45:26.034656+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'aa093056-33a8-491e-9bf0-f7831d0034d6', 'idemp_good_aa093056-33a8-491e-9bf0-f7831d0034d6', 2218.94, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-28T09:23:01.947039+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'a0edc42e-2230-4761-a51c-257c8516e82b', 'idemp_good_a0edc42e-2230-4761-a51c-257c8516e82b', 1988.16, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2025-12-30T17:11:05.623980+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '539e5708-9c0b-413d-9159-49ae54c2032b', 'idemp_good_539e5708-9c0b-413d-9159-49ae54c2032b', 1019.09, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-02T10:31:48.749728+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '68454d0b-6fb0-42e7-b49e-805d911af7d9', 'idemp_good_68454d0b-6fb0-42e7-b49e-805d911af7d9', 1744.25, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-06T11:32:25.395268+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '0fef6303-92f9-4623-a0d5-4e094e73d5e1', 'idemp_good_0fef6303-92f9-4623-a0d5-4e094e73d5e1', 824.51, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-11T11:15:00.710993+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd1a10f90-e531-4c35-a5ae-e0a813352639', 'idemp_good_d1a10f90-e531-4c35-a5ae-e0a813352639', 2051.4, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-13T22:10:51.344749+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '81e6e721-f8de-4c7a-a578-f25d6ecdfd2a', 'idemp_good_81e6e721-f8de-4c7a-a578-f25d6ecdfd2a', 2310.16, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-17T22:46:02.716518+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '75d44ba2-5a17-4f17-bb9c-cd43f9607f0a', 'idemp_good_75d44ba2-5a17-4f17-bb9c-cd43f9607f0a', 609.43, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-20T17:14:50.258214+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'b44b55cf-1fbb-4a2f-a8c6-9301028245af', 'idemp_good_b44b55cf-1fbb-4a2f-a8c6-9301028245af', 1764.12, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-23T04:33:57.664493+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '85fdd9a0-809b-42f0-b026-8fe34f980471', 'idemp_good_85fdd9a0-809b-42f0-b026-8fe34f980471', 1171.03, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-27T11:49:27.533371+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'a9d0de82-5d43-4640-b173-98641fa7f61b', 'idemp_good_a9d0de82-5d43-4640-b173-98641fa7f61b', 1792.25, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-01-30T09:23:11.705673+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'ff2616a7-5794-41f3-9ce1-2ed42a834a36', 'idemp_good_ff2616a7-5794-41f3-9ce1-2ed42a834a36', 2028.97, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-02T04:20:13.681861+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '1e73520c-25e4-43ae-a7b6-2c15492ced31', 'idemp_good_1e73520c-25e4-43ae-a7b6-2c15492ced31', 607.59, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-06T08:54:51.059411+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2f91b15f-219b-45ce-ad03-2deb5d0a95fe', 'idemp_good_2f91b15f-219b-45ce-ad03-2deb5d0a95fe', 1959.55, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-11T05:38:37.584958+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'cbcbe393-525f-4c2e-aa61-8e11b7c0fc5f', 'idemp_good_cbcbe393-525f-4c2e-aa61-8e11b7c0fc5f', 529.81, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-13T21:11:07.786742+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '242d6c85-55bd-4fc5-916f-2043a0e79a7f', 'idemp_good_242d6c85-55bd-4fc5-916f-2043a0e79a7f', 656.38, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-18T09:08:04.416912+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '7c60c73c-1909-4083-bac0-3c6de55c000c', 'idemp_good_7c60c73c-1909-4083-bac0-3c6de55c000c', 2341.26, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-22T02:44:02.405491+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '293d97fd-434c-430f-98cf-bdbc1965e77b', 'idemp_good_293d97fd-434c-430f-98cf-bdbc1965e77b', 981.78, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-02-26T20:28:06.207661+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'a9e29b75-34e5-4f24-a638-2a2d54decaad', 'idemp_good_a9e29b75-34e5-4f24-a638-2a2d54decaad', 728.24, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-01T03:47:23.952775+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '718b965b-7438-4d6e-af0d-041a03515049', 'idemp_good_718b965b-7438-4d6e-af0d-041a03515049', 1832.73, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-05T14:09:12.373646+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '07d33ae2-2583-4d2d-afd7-cd9e5fb11330', 'idemp_good_07d33ae2-2583-4d2d-afd7-cd9e5fb11330', 1203.01, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-10T04:01:44.357620+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd3e31d5a-bb4a-43ff-8d1b-4a2e14307ced', 'idemp_good_d3e31d5a-bb4a-43ff-8d1b-4a2e14307ced', 740.03, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-14T02:33:32.788774+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '3131c057-422e-4908-9c1f-872ec6abae02', 'idemp_good_3131c057-422e-4908-9c1f-872ec6abae02', 2173.9, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-16T14:08:57.939480+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '95844a02-f365-4a36-88ea-2e9fad704ccf', 'idemp_good_95844a02-f365-4a36-88ea-2e9fad704ccf', 1985.43, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-20T23:27:21.091843+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '24ea7977-e6d4-4b65-9233-93a16f6d2106', 'idemp_good_24ea7977-e6d4-4b65-9233-93a16f6d2106', 820.79, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-24T21:11:25.800072+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '86aa6649-aec2-4fc2-8e1d-5359b41fca61', 'idemp_good_86aa6649-aec2-4fc2-8e1d-5359b41fca61', 2252.18, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-03-27T18:05:12.520904+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '269bd5b9-8b58-4a3b-bb7f-29ff211306b3', 'idemp_good_269bd5b9-8b58-4a3b-bb7f-29ff211306b3', 958.78, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-01T09:27:48.480479+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '3723fae1-ffc5-4803-81dc-66ae5940edb3', 'idemp_good_3723fae1-ffc5-4803-81dc-66ae5940edb3', 2236.07, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-06T07:15:53.894741+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '5a5100ec-e28d-4257-941b-f6cd4d78a666', 'idemp_good_5a5100ec-e28d-4257-941b-f6cd4d78a666', 1017.72, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-08T19:08:24.888127+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2cdba975-c0a0-4760-abba-caf514d191f6', 'idemp_good_2cdba975-c0a0-4760-abba-caf514d191f6', 1456.05, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-12T05:59:56.251208+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '7b09ecaf-729e-4036-8598-5ca92f4b9e2e', 'idemp_good_7b09ecaf-729e-4036-8598-5ca92f4b9e2e', 913.81, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-14T06:45:58.833856+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6b14dcda-c8b5-4707-beae-0cd7a75067be', 'idemp_good_6b14dcda-c8b5-4707-beae-0cd7a75067be', 683.11, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-16T17:55:02.495099+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'a6e21347-81f8-4c56-80da-e32c192be8d2', 'idemp_good_a6e21347-81f8-4c56-80da-e32c192be8d2', 1135.72, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-20T11:31:19.265044+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6b6a1e1a-188e-44d4-9dec-17cb423028de', 'idemp_good_6b6a1e1a-188e-44d4-9dec-17cb423028de', 2497.11, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-24T18:12:34.783173+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '531fe382-2922-43cd-ad67-cb9412f6b6d8', 'idemp_good_531fe382-2922-43cd-ad67-cb9412f6b6d8', 1392.41, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-04-28T01:27:56.440624+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '564d64f8-7df7-4f6b-97ec-90d8fa806cd7', 'idemp_good_564d64f8-7df7-4f6b-97ec-90d8fa806cd7', 623.75, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-01T23:36:43.782615+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'c4410c99-76ae-46d8-9cc9-caefc4548788', 'idemp_good_c4410c99-76ae-46d8-9cc9-caefc4548788', 1278.08, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-04T13:19:44.785392+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd558a9b5-752d-483a-a99e-ab95b85a047d', 'idemp_good_d558a9b5-752d-483a-a99e-ab95b85a047d', 666.61, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-08T06:14:08.309858+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6d6af1f3-340a-4b5b-b77a-efe7075ecca6', 'idemp_good_6d6af1f3-340a-4b5b-b77a-efe7075ecca6', 2368.32, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-10T21:18:05.325209+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd022a480-618c-4d90-8079-743353a045d1', 'idemp_good_d022a480-618c-4d90-8079-743353a045d1', 1483.07, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-12T22:29:24.775606+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '1b814af6-d14d-4b81-9a03-ec1eff399a5c', 'idemp_good_1b814af6-d14d-4b81-9a03-ec1eff399a5c', 646.42, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-15T09:15:52.172030+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '5278a072-a4d6-4b08-af29-7fec3ed8c171', 'idemp_good_5278a072-a4d6-4b08-af29-7fec3ed8c171', 2143.69, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-19T06:48:14.293072+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '773f0264-5cb1-42e2-a768-4e1b2c61c9fd', 'idemp_good_773f0264-5cb1-42e2-a768-4e1b2c61c9fd', 2377.77, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-23T17:18:11.769883+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '38925c9d-d761-45a1-bf4d-1962e16f28a6', 'idemp_good_38925c9d-d761-45a1-bf4d-1962e16f28a6', 1087.65, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-28T15:48:36.796968+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '1ec13e16-d7ef-4e8e-b06e-8328ffb2f39f', 'idemp_good_1ec13e16-d7ef-4e8e-b06e-8328ffb2f39f', 1482.27, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-05-30T19:14:44.114981+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '12167401-aabb-40dd-b66e-37dba0c4d273', 'idemp_good_12167401-aabb-40dd-b66e-37dba0c4d273', 1052.43, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-06-03T21:46:57.729741+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '22e7faec-8424-47bb-a2bf-aff039127c96', 'idemp_good_22e7faec-8424-47bb-a2bf-aff039127c96', 722.86, 'GBP', 'good_user_01', 'merchant_trusted', 
        'GB', 'GB', 'device_good_1', '192.168.1.5', 'web', 
        'COMPLETED', '2026-06-06T15:43:54.777551+00:00', '56f292e4-80f1-704a-38f4-42f883cf5d91', 'PAYMENT'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '6682b32d-fbe2-4d1c-b73d-0fe5910d23f4', 'idemp_bad_6682b32d-fbe2-4d1c-b73d-0fe5910d23f4', 3469.94, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'NG', 'CY', 'device_bad_2', '10.0.165.139', 'api', 
        'COMPLETED', '2026-06-05T00:47:20.028682+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '50caa56b-9a22-4a5c-877d-f8651574c47e', 'idemp_bad_50caa56b-9a22-4a5c-877d-f8651574c47e', 1999.76, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.65.8', 'api', 
        'COMPLETED', '2026-06-05T02:38:30.635162+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '85ba86a2-5713-478b-8785-8bdfad26ccd8', 'idemp_bad_85ba86a2-5713-478b-8785-8bdfad26ccd8', 4123.57, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'NG', 'CY', 'device_bad_3', '10.0.175.12', 'api', 
        'COMPLETED', '2026-06-05T03:18:50.370062+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '1a1f9c75-2e2d-4d07-b75f-2622295ec482', 'idemp_bad_1a1f9c75-2e2d-4d07-b75f-2622295ec482', 4568.61, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_2', '10.0.162.82', 'api', 
        'COMPLETED', '2026-06-05T04:40:11.092215+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'e85520d7-c8fa-402a-932a-b5f06a1f3b36', 'idemp_bad_e85520d7-c8fa-402a-932a-b5f06a1f3b36', 2086.2, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.72.220', 'api', 
        'COMPLETED', '2026-06-05T07:10:54.205729+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '89345e90-9ea4-485c-b753-4fb37195ffdc', 'idemp_bad_89345e90-9ea4-485c-b753-4fb37195ffdc', 1985.15, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_2', '10.0.25.108', 'api', 
        'COMPLETED', '2026-06-05T08:58:30.909642+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd550b949-8008-42ab-9421-988c4a136879', 'idemp_bad_d550b949-8008-42ab-9421-988c4a136879', 1297.29, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_2', '10.0.107.72', 'api', 
        'COMPLETED', '2026-06-05T11:15:25.576762+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'dabe88bc-3249-4f39-8933-3daed0b5f53f', 'idemp_bad_dabe88bc-3249-4f39-8933-3daed0b5f53f', 1475.56, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'US', 'CY', 'device_bad_2', '10.0.210.48', 'api', 
        'COMPLETED', '2026-06-05T13:26:09.797228+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '3c70f079-f38b-4ffb-bcc9-e64dce6845b7', 'idemp_bad_3c70f079-f38b-4ffb-bcc9-e64dce6845b7', 4667.95, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_2', '10.0.191.77', 'api', 
        'COMPLETED', '2026-06-05T16:01:12.149131+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '047268c9-1275-4f27-9645-06781f006a81', 'idemp_bad_047268c9-1275-4f27-9645-06781f006a81', 3992.2, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_3', '10.0.199.127', 'api', 
        'COMPLETED', '2026-06-05T16:47:56.777304+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'd6166ef3-d991-4fda-a5fa-1051c5892569', 'idemp_bad_d6166ef3-d991-4fda-a5fa-1051c5892569', 2455.45, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'CN', 'CY', 'device_bad_1', '10.0.59.116', 'api', 
        'COMPLETED', '2026-06-05T19:18:34.953534+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '47bf420e-bba2-48ca-b5c2-c047716cf11f', 'idemp_bad_47bf420e-bba2-48ca-b5c2-c047716cf11f', 4051.75, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'US', 'CY', 'device_bad_1', '10.0.248.226', 'api', 
        'COMPLETED', '2026-06-05T20:54:25.406428+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '2c386573-c018-462b-83d0-2aedca70bc48', 'idemp_bad_2c386573-c018-462b-83d0-2aedca70bc48', 3159.89, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'RU', 'CY', 'device_bad_1', '10.0.28.69', 'api', 
        'COMPLETED', '2026-06-05T23:21:19.523351+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        'fddd55da-ab3c-45cd-a0be-072f2eb20c49', 'idemp_bad_fddd55da-ab3c-45cd-a0be-072f2eb20c49', 1272.83, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'NG', 'CY', 'device_bad_3', '10.0.228.150', 'api', 
        'COMPLETED', '2026-06-06T00:23:49.737496+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    

    INSERT INTO transactions (
        transaction_id, idempotency_key, amount, currency, sender_id, receiver_id, 
        sender_country, receiver_country, device_fingerprint, ip_address, channel, 
        status, created_at, client_id, transaction_type
    ) VALUES (
        '735e5aeb-7492-4d8c-b67d-0344ed87e901', 'idemp_bad_735e5aeb-7492-4d8c-b67d-0344ed87e901', 2521.63, 'USD', 'bad_user_01', 'unknown_crypto_exchange', 
        'GB', 'CY', 'device_bad_4', '10.0.46.215', 'api', 
        'COMPLETED', '2026-06-06T00:54:30.467504+00:00', '5692b244-30d1-7072-584e-1b3637f04ab7', 'CRYPTO_PURCHASE'
    );
    
\connect aegis_risk;

INSERT INTO account_profiles (
    account_id, total_txn_count, total_volume_lifetime, total_volume_30d, txn_count_30d, 
    total_volume_24h, txn_count_24h, txn_count_1h, total_volume_1h, avg_txn_amount, 
    max_txn_amount, is_high_risk, fraud_txn_count, blocked_txn_count, review_txn_count, 
    unique_receiver_count, known_receiver_ids, unique_device_count, known_device_fingerprints, 
    unique_country_count, known_receiver_countries, first_seen_at, last_seen_at, version
) VALUES (
    'good_user_01', 53, 74526.44000000002, 11178.966000000002, 10, 
    0, 0, 0, 0, 1406.1592452830191, 
    5000.00, false, 0, 0, 0, 
    5, ARRAY['merchant_trusted', 'merchant_1', 'merchant_2', 'merchant_3', 'merchant_4'], 1, ARRAY['device_good_1'], 
    1, ARRAY['GB'], '2025-12-09T00:47:20.028682+00:00', '2026-06-06T00:47:20.028682+00:00', 1
);


INSERT INTO account_profiles (
    account_id, total_txn_count, total_volume_lifetime, total_volume_30d, txn_count_30d, 
    total_volume_24h, txn_count_24h, txn_count_1h, total_volume_1h, avg_txn_amount, 
    max_txn_amount, is_high_risk, fraud_txn_count, blocked_txn_count, review_txn_count, 
    unique_receiver_count, known_receiver_ids, unique_device_count, known_device_fingerprints, 
    unique_country_count, known_receiver_countries, first_seen_at, last_seen_at, version
) VALUES (
    'bad_user_01', 15, 43127.780000000006, 43127.780000000006, 15, 
    43127.780000000006, 15, 5, 10000.00, 2875.185333333334, 
    5000.00, true, 2, 5, 8, 
    1, ARRAY['unknown_crypto_exchange'], 4, ARRAY['device_bad_1', 'device_bad_2', 'device_bad_3', 'device_bad_4'], 
    5, ARRAY['RU', 'NG', 'US', 'GB', 'CN'], '2026-06-05T00:47:20.028682+00:00', '2026-06-07T00:47:20.028682+00:00', 15
);
