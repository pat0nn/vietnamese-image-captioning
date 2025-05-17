--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Debian 14.17-1.pgdg120+1)
-- Dumped by pg_dump version 14.17 (Debian 14.17-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pglogical; Type: SCHEMA; Schema: -; Owner: postgres
--



ALTER SCHEMA pglogical OWNER TO postgres;

--
-- Name: pglogical; Type: EXTENSION; Schema: -; Owner: -
--



--
-- Name: EXTENSION pglogical; Type: COMMENT; Schema: -; Owner: 
--



SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: caption_ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.caption_ratings (
    id integer NOT NULL,
    image_id character varying(100) NOT NULL,
    user_id integer,
    rating integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT caption_ratings_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.caption_ratings OWNER TO postgres;

--
-- Name: caption_ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.caption_ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.caption_ratings_id_seq OWNER TO postgres;

--
-- Name: caption_ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.caption_ratings_id_seq OWNED BY public.caption_ratings.id;


--
-- Name: contributions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.contributions (
    id integer NOT NULL,
    user_id integer,
    image_id character varying(100) NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying,
    reviewer_id integer,
    review_notes text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.contributions OWNER TO postgres;

--
-- Name: contributions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.contributions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contributions_id_seq OWNER TO postgres;

--
-- Name: contributions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.contributions_id_seq OWNED BY public.contributions.id;


--
-- Name: daily_stats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.daily_stats (
    id integer NOT NULL,
    date date NOT NULL,
    caption_requests integer DEFAULT 0,
    contributions integer DEFAULT 0,
    ratings integer DEFAULT 0,
    average_rating numeric(3,2) DEFAULT 0.00,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ratings_sum integer DEFAULT 0
);


ALTER TABLE public.daily_stats OWNER TO postgres;

--
-- Name: daily_stats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.daily_stats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.daily_stats_id_seq OWNER TO postgres;

--
-- Name: daily_stats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.daily_stats_id_seq OWNED BY public.daily_stats.id;


--
-- Name: images; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.images (
    id integer NOT NULL,
    image_id character varying(100) NOT NULL,
    image_path character varying(255) NOT NULL,
    user_caption text,
    ai_caption text,
    user_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    storage_type character varying(10) DEFAULT 'local'::character varying
);


ALTER TABLE public.images OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.images_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.images_id_seq OWNER TO postgres;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: model_versions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.model_versions (
    id integer NOT NULL,
    version_name character varying(100) NOT NULL,
    model_path character varying(255) NOT NULL,
    is_active boolean DEFAULT false,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.model_versions OWNER TO postgres;

--
-- Name: model_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.model_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.model_versions_id_seq OWNER TO postgres;

--
-- Name: model_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.model_versions_id_seq OWNED BY public.model_versions.id;


--
-- Name: user_activities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_activities (
    id integer NOT NULL,
    activity_type character varying(50) NOT NULL,
    user_id integer,
    ip_address character varying(50),
    details jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_activities OWNER TO postgres;

--
-- Name: user_activities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_activities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_activities_id_seq OWNER TO postgres;

--
-- Name: user_activities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_activities_id_seq OWNED BY public.user_activities.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    full_name character varying(100),
    biography text,
    is_admin boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    avatar character varying(255),
    storage_type character varying(10) DEFAULT 'local'::character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: caption_ratings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.caption_ratings ALTER COLUMN id SET DEFAULT nextval('public.caption_ratings_id_seq'::regclass);


--
-- Name: contributions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contributions ALTER COLUMN id SET DEFAULT nextval('public.contributions_id_seq'::regclass);


--
-- Name: daily_stats id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats ALTER COLUMN id SET DEFAULT nextval('public.daily_stats_id_seq'::regclass);


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Name: model_versions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_versions ALTER COLUMN id SET DEFAULT nextval('public.model_versions_id_seq'::regclass);


--
-- Name: user_activities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activities ALTER COLUMN id SET DEFAULT nextval('public.user_activities_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: caption_ratings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.caption_ratings (id, image_id, user_id, rating, created_at) FROM stdin;
1	bd35730c-953a-4a8f-a235-a4ca826a445d	\N	4	2025-04-30 10:42:38.368441
2	af341ed3-6215-4cce-ad27-deca8c7ada81	\N	5	2025-04-30 10:46:48.516818
3	6dbe2c7a-6f4f-4a25-95e8-d88aa8dad0ab	\N	5	2025-04-30 10:49:24.954657
4	ecea0490-42de-4d72-8fef-93748767bbdc	\N	5	2025-04-30 10:54:24.679415
5	ecea0490-42de-4d72-8fef-93748767bbdc	\N	5	2025-04-30 10:54:28.537217
6	fca77d1d-670b-421d-8e35-31dc66800ad9	3	4	2025-05-01 17:23:10.790737
7	4275b703-4034-4383-9306-b629356f4115	\N	4	2025-05-01 18:08:06.135115
8	fd39a0fe-3dd9-4aac-a2ad-8ba43ad12085	1	1	2025-05-02 18:20:33.483132
9	35bdba09-d1eb-4a79-beb9-1db2d03edf1c	\N	4	2025-05-04 14:14:46.35328
10	9dc3e3a3-4409-491f-b6c0-5d1187d99158	\N	5	2025-05-04 19:42:18.272069
11	6aea609f-4507-4e67-a4b9-494149cf4ad6	36	5	2025-05-07 12:11:55.289304
12	05daa6d3-51c4-4c4f-9f09-b24e76be52da	36	5	2025-05-09 09:12:26.871724
13	83b0e6da-6611-4477-8260-e6564af04946	1	3	2025-05-09 09:48:32.141663
14	fe393289-3544-46d5-9071-a1410bf302fc	1	4	2025-05-09 09:48:47.417975
15	ac6af231-e50c-44bd-b6d4-1f9b65ea2cf9	1	5	2025-05-09 09:49:06.307926
16	d8f07d3d-3f3f-46d1-9f89-21abdfa67159	1	5	2025-05-09 09:49:26.922791
17	42b9dd17-29d6-4d19-9562-4fb7b8731501	1	5	2025-05-09 09:49:46.758921
18	2906bc1e-91dd-44f7-a207-979fce13f4a9	1	5	2025-05-09 09:50:04.21199
19	46cbc9c6-50d9-4732-8703-08e8426c6a80	1	4	2025-05-09 09:50:26.770733
20	c2f38fc9-741e-47be-b0d3-a6a123caba32	1	5	2025-05-09 09:50:41.675556
21	eceb76e3-3623-4a45-92a8-f61a8f8af683	1	2	2025-05-09 09:51:00.323675
22	def80f03-037a-438b-a66a-99da5c290343	36	5	2025-05-13 13:15:15.71352
\.


--
-- Data for Name: contributions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.contributions (id, user_id, image_id, status, reviewer_id, review_notes, created_at, updated_at) FROM stdin;
67	36	75641388-d952-4bd8-9ca1-da6b7ce667bf.jpg	pending	\N	\N	2025-05-14 03:42:54.156316	2025-05-14 03:42:54.156316
57	36	514398ff-71d3-46ba-81e0-c0be8c87aa90	approved	36		2025-05-08 10:37:35.492621	2025-05-09 09:43:21.696851
56	36	60338027-6f7f-434d-ac68-0732f32cc728	approved	36		2025-05-08 10:28:29.38997	2025-05-09 09:43:22.784446
55	36	03056bdc-7681-49f0-ad1c-59676033d8e4	approved	36		2025-05-07 12:54:28.091689	2025-05-09 09:43:24.854885
66	1	b0bf8cff-62b9-4bb2-b36c-906b2280b21f	pending	\N	\N	2025-05-09 09:59:21.880573	2025-05-09 09:59:21.880573
59	1	f207eeba-3bf0-4ab6-b08d-a1754e540942	approved	36		2025-05-09 09:53:22.063371	2025-05-09 10:07:55.121443
60	1	a69f7d66-5a99-429d-8f29-580866a632b6	approved	36		2025-05-09 09:54:16.9785	2025-05-09 10:07:55.863746
61	1	15e8e83d-093a-4bc7-bb4c-8e01099f0b55	approved	36		2025-05-09 09:54:50.848819	2025-05-09 10:07:58.1151
62	1	d8df917a-f188-433e-84eb-518ad0284dce	rejected	36		2025-05-09 09:55:35.695543	2025-05-09 10:08:00.331103
63	1	a5ea9d65-d259-416e-b555-ec2e1277e67f	approved	36		2025-05-09 09:56:23.413593	2025-05-09 10:08:02.457009
64	1	5a4c0812-333e-4e58-806f-b4c374df5644	rejected	36		2025-05-09 09:57:03.415558	2025-05-09 10:08:03.214359
58	1	1a0629b0-b2f6-471e-9a8a-2743b3821ae8	rejected	36		2025-05-09 09:52:42.830952	2025-05-13 10:24:05.623341
35	3	bf7aa9f9-0878-4e5c-969c-824e04304e3c	approved	1		2025-04-30 12:17:48.761262	2025-05-13 10:27:22.104785
65	1	f1506bfb-675c-4360-9cd3-128cbf9a396f	approved	36		2025-05-09 09:58:31.294025	2025-05-13 13:46:48.188801
68	36	df9a1a8c-d33c-4726-ba93-58e59ed01dd4	pending	\N	\N	2025-05-13 13:50:25.149669	2025-05-13 13:50:25.149669
69	36	f4ea2ed7-7e82-4d35-8c83-fc27cd66b718	approved	36		2025-05-13 13:50:49.97727	2025-05-13 13:51:00.106224
45	1	a44c6ae9-874e-46ac-b5ae-3c4635468401	approved	1		2025-05-04 19:47:27.10392	2025-05-05 06:14:23.931377
44	36	d113b7ca-2425-43d7-802f-d048ce4175f4	approved	1		2025-05-04 19:45:39.039023	2025-05-05 06:14:24.686116
43	1	c95894b4-5b5f-4a7a-a44b-d3903024ce45	approved	1		2025-05-04 19:44:54.267185	2025-05-05 06:14:25.7377
42	36	35d438ac-541f-4ee7-b3b3-026e518f89cb	approved	1		2025-05-04 19:44:28.588881	2025-05-05 06:14:26.489151
50	36	56ab3337-d883-4aa5-879b-a71a7646ec6e	approved	1		2025-05-05 13:14:09.807409	2025-05-05 13:25:22.567281
53	1	789c2945-b188-4e76-ab04-b985045ea25c	approved	1		2025-05-05 14:15:55.123174	2025-05-05 14:16:02.924162
\.


--
-- Data for Name: daily_stats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.daily_stats (id, date, caption_requests, contributions, ratings, average_rating, created_at, updated_at, ratings_sum) FROM stdin;
6	2025-05-08	21	4	1	0.00	2025-05-07 11:52:10.815514	2025-05-07 11:52:10.815514	5
9	2025-05-13	7	3	1	0.00	2025-05-13 09:18:58.470571	2025-05-13 09:18:58.470571	5
1	2025-05-01	15	9	2	0.00	2025-04-30 10:42:30.323239	2025-04-30 10:42:30.323239	10
2	2025-05-02	4	0	2	0.00	2025-05-01 17:21:24.166936	2025-05-01 17:21:24.166936	8
3	2025-05-03	4	0	1	0.00	2025-05-02 18:12:39.718932	2025-05-02 18:12:39.718932	1
4	2025-05-05	16	4	2	0.00	2025-05-04 11:00:46.784148	2025-05-04 11:00:46.784148	9
5	2025-05-06	18	8	0	0.00	2025-05-04 20:03:42.469406	2025-05-04 20:03:42.469406	0
7	2025-05-09	19	9	10	0.00	2025-05-09 08:51:20.618802	2025-05-09 08:51:20.618802	43
8	2025-05-12	6	0	0	0.00	2025-05-12 16:47:37.942278	2025-05-12 16:47:37.942278	0
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.images (id, image_id, image_path, user_caption, ai_caption, user_id, created_at, updated_at, storage_type) FROM stdin;
170	c5e28d40-8968-4f3b-9cea-e2003ef1e8d2	c5e28d40-8968-4f3b-9cea-e2003ef1e8d2.jpg	\N	Có một cô gái mặc váy chấm bi đang tạo dáng chụp ảnh trên đường.	\N	2025-05-13 09:18:58.451654	2025-05-13 09:18:58.451654	gcs
142	00330ac3-1531-4122-a23f-eadb377c2c09	00330ac3-1531-4122-a23f-eadb377c2c09.jpg	\N	Có nhiều người đang xuất hiện ở bên trong một siêu thị.	\N	2025-05-09 09:14:28.466684	2025-05-09 09:14:28.466684	gcs
81	c95894b4-5b5f-4a7a-a44b-d3903024ce45	c95894b4-5b5f-4a7a-a44b-d3903024ce45.jpg	e e e e e e e e	\N	1	2025-05-04 19:44:54.261895	2025-05-04 19:44:54.261895	gcs
132	cd634d5b-56d8-4407-9e3f-271a7f555a6d	cd634d5b-56d8-4407-9e3f-271a7f555a6d.jpg	\N	Đây là bức ảnh chụp giao diện của một ứng dụng.	\N	2025-05-08 15:11:03.487514	2025-05-08 15:11:03.487514	gcs
73	026d0d33-c907-4505-8eef-72f36106034f	026d0d33-c907-4505-8eef-72f36106034f.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 14:09:00.127703	2025-05-04 14:09:00.127703	gcs
173	090efaad-4367-4ed7-9a63-60feff89aed6	090efaad-4367-4ed7-9a63-60feff89aed6.jpg	\N	Có một người phụ nữ đang đứng bên quầy hàng trái cây.	\N	2025-05-13 13:03:50.596281	2025-05-13 13:03:50.596281	gcs
154	1a0629b0-b2f6-471e-9a8a-2743b3821ae8	1a0629b0-b2f6-471e-9a8a-2743b3821ae8.jpg	Có một người đàn ông khoác túi đeo chéo đang đi về phía bức tường	\N	1	2025-05-09 09:52:42.825892	2025-05-09 09:52:42.825892	gcs
83	d113b7ca-2425-43d7-802f-d048ce4175f4	d113b7ca-2425-43d7-802f-d048ce4175f4.jpg	Có một bể cá đang được thắp sáng	\N	36	2025-05-04 19:45:39.033994	2025-05-04 19:45:39.033994	gcs
148	d8f07d3d-3f3f-46d1-9f89-21abdfa67159	d8f07d3d-3f3f-46d1-9f89-21abdfa67159.jpg	\N	Ở trên vũng lầy có sự xuất hiện của một nhóm người.	\N	2025-05-09 09:49:23.025368	2025-05-09 09:49:23.025368	gcs
136	e6aa7b82-a463-4ced-a8e2-e59e674e7b80	e6aa7b82-a463-4ced-a8e2-e59e674e7b80.jpg	\N	Có một cái mô hình xe buýt xuất hiện ở trong bức ảnh.	\N	2025-05-09 08:51:20.599633	2025-05-09 08:51:20.599633	gcs
75	eb9fc3ed-c439-46b5-acf7-2dfe32ae3fe1	eb9fc3ed-c439-46b5-acf7-2dfe32ae3fe1.jpg	\N	Ở trên vỉa hè có sự xuất hiện của nhiều cây xanh.	\N	2025-05-04 14:14:18.773354	2025-05-04 14:14:18.773354	gcs
179	f4ea2ed7-7e82-4d35-8c83-fc27cd66b718	f4ea2ed7-7e82-4d35-8c83-fc27cd66b718.jpg	Có một người đang cưỡi ngựa trong cuộc thi đua ngựa	\N	36	2025-05-13 13:50:49.96649	2025-05-13 13:50:49.96649	gcs
164	f52973bc-ed62-4b55-8547-6e09d462c1bd	f52973bc-ed62-4b55-8547-6e09d462c1bd.jpg	\N	Người phụ nữ bán thịt heo mặc tạp dề màu đỏ.	\N	2025-05-12 16:47:37.920781	2025-05-12 16:47:37.920781	gcs
76	35bdba09-d1eb-4a79-beb9-1db2d03edf1c	35bdba09-d1eb-4a79-beb9-1db2d03edf1c.jpg	\N	Ở trong căn phòng có sự xuất hiện của một vài bức ảnh.	\N	2025-05-04 14:14:37.458753	2025-05-04 14:14:37.458753	gcs
80	35d438ac-541f-4ee7-b3b3-026e518f89cb	35d438ac-541f-4ee7-b3b3-026e518f89cb.jpg	Hình ảnh phía trước một quán kemm	\N	36	2025-05-04 19:44:28.583975	2025-05-04 19:44:28.583975	gcs
72	441165fb-029f-409b-9c1a-a4ebcfbeddbf	441165fb-029f-409b-9c1a-a4ebcfbeddbf.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 13:55:59.286834	2025-05-04 13:55:59.286834	gcs
160	5a4c0812-333e-4e58-806f-b4c374df5644	5a4c0812-333e-4e58-806f-b4c374df5644.jpg	Có một ca sĩ đang đứng biểu diễn ở trên sân khấu	\N	1	2025-05-09 09:57:03.410412	2025-05-09 09:57:03.410412	gcs
130	60338027-6f7f-434d-ac68-0732f32cc728	60338027-6f7f-434d-ac68-0732f32cc728.jpg	Có một chiếc chuột led rgb trong bức hình 	\N	36	2025-05-08 10:28:29.384887	2025-05-08 10:28:29.384887	gcs
82	924c0e05-4b4a-433f-9b50-a6e58e913875	924c0e05-4b4a-433f-9b50-a6e58e913875.jpg	\N	Có một cái mô hình thuyền xuất hiện ở trong bức ảnh.	\N	2025-05-04 19:45:20.265089	2025-05-04 19:45:20.265089	gcs
79	9dc3e3a3-4409-491f-b6c0-5d1187d99158	9dc3e3a3-4409-491f-b6c0-5d1187d99158.jpg	\N	Có một người đàn ông đang đi bộ ở phía trước bức tường.	\N	2025-05-04 19:42:10.027647	2025-05-04 19:42:10.027647	gcs
78	b3327abf-1072-4e96-93a2-f7f9b63ae37d	b3327abf-1072-4e96-93a2-f7f9b63ae37d.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một dòng chữ màu trắng.	\N	2025-05-04 14:47:27.286374	2025-05-04 14:47:27.286374	gcs
74	b5b3849f-b56b-4c81-9f5e-340089e7b8b5	b5b3849f-b56b-4c81-9f5e-340089e7b8b5.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một dòng chữ màu trắng.	\N	2025-05-04 14:11:13.661802	2025-05-04 14:11:13.661802	gcs
56	8fef23e3-83fb-44c5-9a2b-9359b1b54f39	8fef23e3-83fb-44c5-9a2b-9359b1b54f39.jpg	\N	Có một người phụ nữ mặc áo xám đang nhìn vào một cái màn hình máy tính.	\N	2025-04-30 17:59:06.592705	2025-04-30 17:59:06.592705	gcs
55	09915551-4274-4f1e-ae61-2ef29cc9ecf0	09915551-4274-4f1e-ae61-2ef29cc9ecf0.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-04-30 17:58:30.522545	2025-04-30 17:58:30.522545	gcs
54	15c0c241-15cc-4f7a-8140-2da386f9840d	15c0c241-15cc-4f7a-8140-2da386f9840d.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-04-30 17:57:59.49659	2025-04-30 17:57:59.49659	gcs
171	22d9aded-e03f-4e0e-98cd-85b260316a27	22d9aded-e03f-4e0e-98cd-85b260316a27.jpg	\N	Ở trên mặt nước có sự xuất hiện của những con thuyền chở hàng.	\N	2025-05-13 09:19:30.951278	2025-05-13 09:19:30.951278	gcs
149	42b9dd17-29d6-4d19-9562-4fb7b8731501	42b9dd17-29d6-4d19-9562-4fb7b8731501.jpg	\N	Ở trên sông có sự xuất hiện của một nhóm người đang di chuyển bằng thúng.	\N	2025-05-09 09:49:39.725439	2025-05-09 09:49:39.725439	gcs
88	433d3af5-5e5a-4c3c-8a12-07339bcc1c44	433d3af5-5e5a-4c3c-8a12-07339bcc1c44.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:18:57.330211	2025-05-04 20:18:57.330211	gcs
51	4c9c8b1a-831f-42ae-86b7-188655e87392	4c9c8b1a-831f-42ae-86b7-188655e87392.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	1	2025-04-30 17:45:29.562331	2025-04-30 17:45:29.562331	gcs
131	514398ff-71d3-46ba-81e0-c0be8c87aa90	514398ff-71d3-46ba-81e0-c0be8c87aa90.jpg	Có hai con vịt đang đứng ở trên đường	\N	36	2025-05-08 10:37:35.487433	2025-05-08 10:37:35.487433	gcs
143	561e5ee8-7f7c-4d4b-a65f-5a09aa3cd63d	561e5ee8-7f7c-4d4b-a65f-5a09aa3cd63d.jpg	\N	Có một cái cột cờ xuất hiện ở trong bức ảnh.	\N	2025-05-09 09:17:00.074904	2025-05-09 09:17:00.074904	gcs
50	7b1928bc-f73d-4d09-be9e-ace243d6794b	7b1928bc-f73d-4d09-be9e-ace243d6794b.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	3	2025-04-30 17:43:12.117633	2025-04-30 17:43:12.117633	gcs
165	93d7cb36-c1f7-4612-b3b6-036e16b52c6e	93d7cb36-c1f7-4612-b3b6-036e16b52c6e.jpg	\N	Có một người phụ nữ mặc áo xanh lá cây đang đứng bên trong quầy hàng.	\N	2025-05-12 16:47:48.994451	2025-05-12 16:47:48.994451	gcs
84	a44c6ae9-874e-46ac-b5ae-3c4635468401	a44c6ae9-874e-46ac-b5ae-3c4635468401.jpg	were erer wer werwer  ewrew	\N	1	2025-05-04 19:47:27.098526	2025-05-04 19:47:27.098526	gcs
174	def80f03-037a-438b-a66a-99da5c290343	def80f03-037a-438b-a66a-99da5c290343.jpg	\N	Có một cái cột cờ xuất hiện ở trong bức ảnh.	\N	2025-05-13 13:15:13.359689	2025-05-13 13:15:13.359689	gcs
133	a7b7bc5b-9ff4-4a29-8f0e-c2c222a434af	a7b7bc5b-9ff4-4a29-8f0e-c2c222a434af.jpg	\N	Đây là khung cảnh xuất hiện ở bên trong một cửa hàng.	\N	2025-05-08 15:11:20.577077	2025-05-08 15:11:20.577077	gcs
57	bbeea78f-7229-4d8a-a53d-1bc1b94244b3	bbeea78f-7229-4d8a-a53d-1bc1b94244b3.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	3	2025-05-01 17:21:24.147344	2025-05-01 17:21:24.147344	gcs
53	be436a0e-dace-4187-8c25-cdf179978371	be436a0e-dace-4187-8c25-cdf179978371.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	1	2025-04-30 17:48:40.998561	2025-04-30 17:48:40.998561	gcs
91	e9c4062b-ddf9-41ee-b8ac-5d82eddb719b	e9c4062b-ddf9-41ee-b8ac-5d82eddb719b.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:21:15.386406	2025-05-04 20:21:15.386406	gcs
52	ea07c7a0-1cf8-4ac7-81b8-a0f0c31b5fbd	ea07c7a0-1cf8-4ac7-81b8-a0f0c31b5fbd.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-04-30 17:47:27.255623	2025-04-30 17:47:27.255623	gcs
90	beaadd09-095a-4f23-aedf-470895b3cb96	beaadd09-095a-4f23-aedf-470895b3cb96.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:20:52.31223	2025-05-04 20:20:52.31223	gcs
137	c231010e-65b2-43a4-96ed-4d0d728eb500	c231010e-65b2-43a4-96ed-4d0d728eb500.jpg	\N	Có nhiều người đang đứng xung quanh quầy hàng hoa quả.	\N	2025-05-09 09:02:53.165604	2025-05-09 09:02:53.165604	gcs
49	ec6ffe7a-91de-4238-b7ae-dbd1d9faadd7	ec6ffe7a-91de-4238-b7ae-dbd1d9faadd7.jpg	\N	Đây là khung cảnh nhìn từ trên cao của một khu di tích.	\N	2025-04-30 17:42:13.775948	2025-04-30 17:42:13.775948	gcs
89	d7f9d43f-0577-48cd-97ea-ba3c1da68fe4	d7f9d43f-0577-48cd-97ea-ba3c1da68fe4.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:20:35.145885	2025-05-04 20:20:35.145885	gcs
161	f1506bfb-675c-4360-9cd3-128cbf9a396f	f1506bfb-675c-4360-9cd3-128cbf9a396f.jpg	Một chiếc bể thủy sinh trên bàn đang được thắp đèn	\N	1	2025-05-09 09:58:31.288826	2025-05-09 09:58:31.288826	gcs
155	f207eeba-3bf0-4ab6-b08d-a1754e540942	f207eeba-3bf0-4ab6-b08d-a1754e540942.jpg	Ở trong bức ảnh có sự xuất hiện của một tấm bia đá khắc chữ	\N	1	2025-05-09 09:53:22.058278	2025-05-09 09:53:22.058278	gcs
58	fca77d1d-670b-421d-8e35-31dc66800ad9	fca77d1d-670b-421d-8e35-31dc66800ad9.jpg	\N	Có một người đàn ông mặc áo đen đang ngồi bên một cái bàn làm việc.	3	2025-05-01 17:23:06.303948	2025-05-01 17:23:06.303948	gcs
125	03056bdc-7681-49f0-ad1c-59676033d8e4	03056bdc-7681-49f0-ad1c-59676033d8e4.jpg	Đây là một chiếc bể thủy sinh	\N	36	2025-05-07 12:54:28.086398	2025-05-07 12:54:28.086398	gcs
134	06667e1b-f40f-49b4-8c6b-fc8d9a401cba	06667e1b-f40f-49b4-8c6b-fc8d9a401cba.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh lá cây.	\N	2025-05-08 15:12:13.294059	2025-05-08 15:12:13.294059	gcs
94	0b212e77-12b9-4c5c-85d1-2604bd7d40d7	0b212e77-12b9-4c5c-85d1-2604bd7d40d7.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:23:58.141993	2025-05-04 20:23:58.141993	gcs
150	2906bc1e-91dd-44f7-a207-979fce13f4a9	2906bc1e-91dd-44f7-a207-979fce13f4a9.jpg	\N	Ở trên quầy hàng có sự xuất hiện của nhiều loại rau.	\N	2025-05-09 09:49:59.777385	2025-05-09 09:49:59.777385	gcs
123	58ad701c-0dc3-4f4d-a47e-f14aadcead93	58ad701c-0dc3-4f4d-a47e-f14aadcead93.jpg	\N	Có một cái cột điện xuất hiện ở trước ngôi nhà.	\N	2025-05-07 12:48:11.298342	2025-05-07 12:48:11.298342	gcs
126	65e93a55-d4ee-40aa-8bc4-755ed6608691	65e93a55-d4ee-40aa-8bc4-755ed6608691.jpg	\N	Có một người đàn ông đang ngồi bên trong một cái tủ kính.	\N	2025-05-07 12:55:10.558732	2025-05-07 12:55:10.558732	gcs
144	782cb38f-e0e5-4786-acd5-a4710cf53c7a	782cb38f-e0e5-4786-acd5-a4710cf53c7a.jpg	\N	Có một cái cột cờ xuất hiện ở trong bức ảnh.	\N	2025-05-09 09:17:48.390719	2025-05-09 09:17:48.390719	gcs
109	789c2945-b188-4e76-ab04-b985045ea25c	789c2945-b188-4e76-ab04-b985045ea25c.jpg	Cớ một người đàn ông đang ăn phở	\N	1	2025-05-05 14:15:55.118112	2025-05-05 14:15:55.118112	gcs
166	856d18f2-00fa-422c-8f13-45c3d02bce6b	856d18f2-00fa-422c-8f13-45c3d02bce6b.jpg	\N	Có hai người đang chơi nhảy dù ở trên biển.	\N	2025-05-12 16:49:07.826736	2025-05-12 16:49:07.826736	gcs
156	a69f7d66-5a99-429d-8f29-580866a632b6	a69f7d66-5a99-429d-8f29-580866a632b6.jpg	Có một nhóm người đang vui chơi dưới một mái vòm có trang trí đèn	\N	1	2025-05-09 09:54:16.97328	2025-05-09 09:54:16.97328	gcs
162	b0bf8cff-62b9-4bb2-b36c-906b2280b21f	b0bf8cff-62b9-4bb2-b36c-906b2280b21f.jpg	Đây là khung cảnh phía trước một nhà thờ vào buổi tối	\N	1	2025-05-09 09:59:21.875422	2025-05-09 09:59:21.875422	gcs
175	b3ba2c10-68bf-488b-9da2-e436b71c37f6	b3ba2c10-68bf-488b-9da2-e436b71c37f6.jpg	\N	Có một cô gái đang đứng trước tấm bảng thông báo.	\N	2025-05-13 13:29:57.971522	2025-05-13 13:29:57.971522	gcs
93	bca7a5fa-2394-44a6-a34a-81d5920e0137	bca7a5fa-2394-44a6-a34a-81d5920e0137.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:22:21.549019	2025-05-04 20:22:21.549019	gcs
138	ea82a8ba-89e4-4e58-86b8-21f17833d41b	ea82a8ba-89e4-4e58-86b8-21f17833d41b.jpg	\N	Có nhiều bức ảnh được treo ở trên tường của căn phòng.	\N	2025-05-09 09:05:59.293372	2025-05-09 09:05:59.293372	gcs
95	f3449afd-c47e-4a53-8a37-ca2ccb64e3d5	f3449afd-c47e-4a53-8a37-ca2ccb64e3d5.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:26:15.972941	2025-05-04 20:26:15.972941	gcs
92	fa5435ec-e4db-4086-95f2-001d177c0242	fa5435ec-e4db-4086-95f2-001d177c0242.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:21:27.403499	2025-05-04 20:21:27.403499	gcs
172	adc994ad-6020-4111-9923-5415ff5df733.jpg	adc994ad-6020-4111-9923-5415ff5df733.jpg	\N	Đây là khung cảnh nhìn từ trên cao của một khu di tích.	\N	2025-05-14 03:21:22.487794	2025-05-14 03:21:22.487794	gcs
62	7d025169-bdeb-4b1a-956d-779f7d297d4c	7d025169-bdeb-4b1a-956d-779f7d297d4c.jpg	\N	Ở trên vũng lầy có sự xuất hiện của một nhóm người.	\N	2025-05-02 18:13:28.252966	2025-05-02 18:13:28.252966	gcs
129	0dffe044-e27e-48e7-b8ca-1fa9f6ba516b	0dffe044-e27e-48e7-b8ca-1fa9f6ba516b.jpg	\N	Có một chiếc xe đang được dựng ở bên một cái tủ kính.	\N	2025-05-07 13:01:32.456108	2025-05-07 13:01:32.456108	gcs
106	0f12474a-b8ba-466a-8d23-42acab2d72f8	0f12474a-b8ba-466a-8d23-42acab2d72f8.jpg	\N	Có một người phụ nữ mặc áo xanh dương đang đứng bên quầy hàng trái cây.	\N	2025-05-05 14:13:36.215199	2025-05-05 14:13:36.215199	gcs
157	15e8e83d-093a-4bc7-bb4c-8e01099f0b55	15e8e83d-093a-4bc7-bb4c-8e01099f0b55.jpg	Có một người phụ nữ đang chọn hoa quả trong siêu thị	\N	1	2025-05-09 09:54:50.843696	2025-05-09 09:54:50.843696	gcs
128	1def30bc-b2ed-476c-b9f7-c79df9a475a4	1def30bc-b2ed-476c-b9f7-c79df9a475a4.jpg	\N	Có một chậu cây đang được đặt ở giữa căn nhà.	\N	2025-05-07 13:00:59.007655	2025-05-07 13:00:59.007655	gcs
145	83b0e6da-6611-4477-8260-e6564af04946	83b0e6da-6611-4477-8260-e6564af04946.jpg	\N	Ở phía trước khu chợ có sự xuất hiện của nhiều phương tiện giao thông.	\N	2025-05-09 09:48:23.866857	2025-05-09 09:48:23.866857	gcs
70	929618be-5a61-4818-bc65-998c541edb50	929618be-5a61-4818-bc65-998c541edb50.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 13:16:00.06979	2025-05-04 13:16:00.06979	gcs
61	3db14e35-4136-4a75-9976-33cf7ee4d6a7	3db14e35-4136-4a75-9976-33cf7ee4d6a7.jpg	\N	Có nhiều hộp hoa quả xuất hiện ở trước mặt hai cô gái.	\N	2025-05-02 18:12:39.681455	2025-05-02 18:12:39.681455	gcs
60	9a1d0c3c-2e99-47ed-bec6-850aee1c2caf	9a1d0c3c-2e99-47ed-bec6-850aee1c2caf.jpg	\N	Có một người đàn ông đang đẩy một chiếc xe đẩy siêu thị.	\N	2025-05-01 18:25:46.591264	2025-05-01 18:25:46.591264	gcs
163	c4129c3f-01c4-4028-b1a1-b3a6b288a1cf	c4129c3f-01c4-4028-b1a1-b3a6b288a1cf.jpg	\N	Có một cô gái đang đứng ở trước một kệ hàng.	\N	2025-05-09 10:01:40.454925	2025-05-09 10:01:40.454925	gcs
59	4275b703-4034-4383-9306-b629356f4115	4275b703-4034-4383-9306-b629356f4115.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-01 18:07:50.834809	2025-05-01 18:07:50.834809	gcs
66	42f94d8f-e342-44ce-9e10-b3cb70160191	42f94d8f-e342-44ce-9e10-b3cb70160191.jpg	\N	Có một người đàn ông mặc áo đen đang ngồi bên một cái bàn làm việc.	\N	2025-05-04 11:02:22.235727	2025-05-04 11:02:22.235727	gcs
151	46cbc9c6-50d9-4732-8703-08e8426c6a80	46cbc9c6-50d9-4732-8703-08e8426c6a80.jpg	\N	Có nhiều người đang ngồi ở dưới một cái mái hiên.	\N	2025-05-09 09:50:21.848129	2025-05-09 09:50:21.848129	gcs
77	4935a7bb-26fc-4a91-ada2-ed5e425e25b7	4935a7bb-26fc-4a91-ada2-ed5e425e25b7.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 14:36:47.915415	2025-05-04 14:36:47.915415	gcs
112	4cf1b615-be92-4f2d-b01d-3fe6122fb2f6	4cf1b615-be92-4f2d-b01d-3fe6122fb2f6.jpg	\N	Có một cô gái đang ngồi ở trên một cái ghế nhựa màu xanh.	\N	2025-05-07 11:52:22.283019	2025-05-07 11:52:22.283019	gcs
176	4d3e8545-b42d-4032-b570-302487fa1b1d	4d3e8545-b42d-4032-b570-302487fa1b1d.jpg	\N	Có một cô gái đang đứng trước tấm bảng thông báo.	\N	2025-05-13 13:49:44.049065	2025-05-13 13:49:44.049065	gcs
71	53d583af-5731-4580-b61f-059e43917e50	53d583af-5731-4580-b61f-059e43917e50.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 13:28:15.799046	2025-05-04 13:28:15.799046	gcs
127	6c83b55d-752e-4f3b-9d45-7da8a8de9b52	6c83b55d-752e-4f3b-9d45-7da8a8de9b52.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một cái mô hình xe buýt.	\N	2025-05-07 12:56:35.846639	2025-05-07 12:56:35.846639	gcs
107	8ef3fbde-57c8-4d65-a896-9fd776b32584	8ef3fbde-57c8-4d65-a896-9fd776b32584.jpg	\N	Có một cô gái mặc áo vàng đang dựa tay vào lan can.	\N	2025-05-05 14:14:21.478891	2025-05-05 14:14:21.478891	gcs
113	8f25d618-b40f-46cd-98dc-87be4f252b70	8f25d618-b40f-46cd-98dc-87be4f252b70.jpg	\N	Ở trên mặt nước có sự xuất hiện của một con thuyền.	\N	2025-05-07 11:52:31.627568	2025-05-07 11:52:31.627568	gcs
167	a3221fd4-c52e-45f3-b2b8-a29c2875c5ae	a3221fd4-c52e-45f3-b2b8-a29c2875c5ae.jpg	\N	Có hai người phụ nữ đang cầm trên tay những món đồ lưu niệm.	\N	2025-05-12 16:49:19.993514	2025-05-12 16:49:19.993514	gcs
68	a7abe65d-022b-4aa2-8b4a-d296507e58ed	a7abe65d-022b-4aa2-8b4a-d296507e58ed.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 12:16:16.628406	2025-05-04 12:16:16.628406	gcs
139	b46ccf97-34ae-464d-a99f-7fd5a3efa323	b46ccf97-34ae-464d-a99f-7fd5a3efa323.jpg	\N	Ở trên bãi biển có sự xuất hiện của một nhóm người.	\N	2025-05-09 09:08:53.673192	2025-05-09 09:08:53.673192	gcs
1	bd35730c-953a-4a8f-a235-a4ca826a445d	bd35730c-953a-4a8f-a235-a4ca826a445d.jpg	\N	Có một người phụ nữ đang đứng bên quầy hàng trái cây.	\N	2025-04-30 10:42:30.307151	2025-04-30 10:42:30.307151	gcs
65	c385eefe-d61b-4475-80d0-5428804d90fe	c385eefe-d61b-4475-80d0-5428804d90fe.jpg	\N	Có một người đàn ông mặc áo đen đang ngồi bên một cái bàn làm việc.	\N	2025-05-04 11:00:46.765947	2025-05-04 11:00:46.765947	gcs
135	e40ae8e3-a88c-40eb-b46c-6d25e552005c	e40ae8e3-a88c-40eb-b46c-6d25e552005c.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng và một dòng chữ màu trắng.	\N	2025-05-08 15:12:13.630865	2025-05-08 15:12:13.630865	gcs
42	e8165b43-3e6a-4208-af76-235c87fdcb57	e8165b43-3e6a-4208-af76-235c87fdcb57.jpg	\N	Có một người phụ nữ đang đứng bên quầy hàng trái cây.	\N	2025-04-30 12:18:47.476922	2025-04-30 12:18:47.476922	gcs
69	ebebc713-7129-44d0-bfdb-ed928939133e	ebebc713-7129-44d0-bfdb-ed928939133e.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-05-04 12:43:40.229022	2025-05-04 12:43:40.229022	gcs
63	ec9ceaa7-1617-4e68-ab7f-1c12ce70ea81	ec9ceaa7-1617-4e68-ab7f-1c12ce70ea81.jpg	\N	Có một cô gái mặc áo trắng xuất hiện ở bên kệ hàng.	\N	2025-05-02 18:18:59.821579	2025-05-02 18:18:59.821579	gcs
64	fd39a0fe-3dd9-4aac-a2ad-8ba43ad12085	fd39a0fe-3dd9-4aac-a2ad-8ba43ad12085.jpg	\N	Ở trên cái mẹt có sự xuất hiện của nhiều món ăn.	\N	2025-05-02 18:20:28.003151	2025-05-02 18:20:28.003151	gcs
97	c292680c-a3b5-410b-aa88-20be596b1965	c292680c-a3b5-410b-aa88-20be596b1965.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:29:04.592958	2025-05-04 20:29:04.592958	gcs
140	05daa6d3-51c4-4c4f-9f09-b24e76be52da	05daa6d3-51c4-4c4f-9f09-b24e76be52da.jpg	\N	Có một chiếc thuyền đang di chuyển trên mặt nước.	\N	2025-05-09 09:11:02.854328	2025-05-09 09:11:02.854328	gcs
122	08fd84ed-30a1-4558-8de9-62dfc99847b6	08fd84ed-30a1-4558-8de9-62dfc99847b6.jpg	\N	Có một chiếc xe đang được dựng ở bên một cái tủ kính.	\N	2025-05-07 12:46:24.719011	2025-05-07 12:46:24.719011	gcs
152	c2f38fc9-741e-47be-b0d3-a6a123caba32	c2f38fc9-741e-47be-b0d3-a6a123caba32.jpg	\N	Ở trên ruộng bậc thang có sự xuất hiện của những cái chòi.	\N	2025-05-09 09:50:37.055948	2025-05-09 09:50:37.055948	gcs
117	226851ab-3921-4bb9-bf51-c5ef6b5cb395	226851ab-3921-4bb9-bf51-c5ef6b5cb395.jpg	\N	Ở trong bức ảnh bên trái có sự xuất hiện của hai bức ảnh nhỏ.	\N	2025-05-07 12:08:49.199382	2025-05-07 12:08:49.199382	gcs
108	3177c03a-da65-4530-ac88-1e4c08f0224d	3177c03a-da65-4530-ac88-1e4c08f0224d.jpg	\N	Đây là khung cảnh nhìn từ trên cao của một khu di tích.	\N	2025-05-05 14:14:50.644091	2025-05-05 14:14:50.644091	gcs
96	3ac9fdfe-eeba-48b6-8cd7-308f4da93355	3ac9fdfe-eeba-48b6-8cd7-308f4da93355.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:26:18.875519	2025-05-04 20:26:18.875519	gcs
101	54cf140e-6374-4d45-8cf0-5395231463cf	54cf140e-6374-4d45-8cf0-5395231463cf.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-05 04:58:43.77126	2025-05-05 04:58:43.77126	gcs
118	55e1c32d-6876-4a53-8883-915512d39645	55e1c32d-6876-4a53-8883-915512d39645.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một cái cây cổ thụ.	\N	2025-05-07 12:11:13.645761	2025-05-07 12:11:13.645761	gcs
98	57224543-065a-4242-bb9c-5a002d77ea68	57224543-065a-4242-bb9c-5a002d77ea68.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một biểu tượng màu xanh dương.	\N	2025-05-04 20:29:18.505513	2025-05-04 20:29:18.505513	gcs
119	6aea609f-4507-4e67-a4b9-494149cf4ad6	6aea609f-4507-4e67-a4b9-494149cf4ad6.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một cái cổng.	\N	2025-05-07 12:11:43.151531	2025-05-07 12:11:43.151531	gcs
114	6db76e18-6d8d-4c3c-b6a2-fa5a086e0955	6db76e18-6d8d-4c3c-b6a2-fa5a086e0955.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một người đàn ông.	\N	2025-05-07 12:02:25.698586	2025-05-07 12:02:25.698586	gcs
47	f3660bfa-4eb5-4f7a-bdac-5e2dcc9b1966	f3660bfa-4eb5-4f7a-bdac-5e2dcc9b1966.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	3	2025-04-30 17:40:48.028441	2025-04-30 17:40:48.028441	gcs
177	8d28dca7-b55d-49dc-a707-37fc0ffb4375	8d28dca7-b55d-49dc-a707-37fc0ffb4375.jpg	\N	Ở trên đường có sự xuất hiện của một chiếc xe máy.	\N	2025-05-13 13:50:03.871974	2025-05-13 13:50:03.871974	gcs
158	d8df917a-f188-433e-84eb-518ad0284dce	d8df917a-f188-433e-84eb-518ad0284dce.jpg	Có một con mèo đang nằm phơi nắng ở trên sân	\N	1	2025-05-09 09:55:35.690494	2025-05-09 09:55:35.690494	gcs
3	6dbe2c7a-6f4f-4a25-95e8-d88aa8dad0ab	6dbe2c7a-6f4f-4a25-95e8-d88aa8dad0ab.jpg	\N	Có một người phụ nữ đang đứng bên quầy hàng trái cây.	\N	2025-04-30 10:49:20.529668	2025-04-30 10:49:20.529668	gcs
115	e546487d-7075-4c28-baa1-c8f8e91b12fc	e546487d-7075-4c28-baa1-c8f8e91b12fc.jpg	\N	Có một người đàn ông đang ngồi ở trên một cái ghế nhựa màu xanh.	\N	2025-05-07 12:02:47.331694	2025-05-07 12:02:47.331694	gcs
116	7e7b811f-79d7-4191-a2c4-285c8c350df3	7e7b811f-79d7-4191-a2c4-285c8c350df3.jpg	\N	Ở trong ảnh có sự xuất hiện của một đoạn văn bản màu trắng.	\N	2025-05-07 12:07:50.450659	2025-05-07 12:07:50.450659	gcs
67	a38bf6d5-63ed-48ee-b073-9dfe2680889b	a38bf6d5-63ed-48ee-b073-9dfe2680889b.jpg	\N	Có nhiều xe cộ đang di chuyển ở trên đường.	\N	2025-05-04 12:13:58.464229	2025-05-04 12:13:58.464229	gcs
146	fe393289-3544-46d5-9071-a1410bf302fc	fe393289-3544-46d5-9071-a1410bf302fc.jpg	\N	Có những cột đá xuất hiện ở trong căn phòng.	\N	2025-05-09 09:48:43.10889	2025-05-09 09:48:43.10889	gcs
102	a71135c5-9225-4d5a-aa98-429c666be28e	a71135c5-9225-4d5a-aa98-429c666be28e.jpg	\N	Đây là ảnh chụp giao diện của một ứng dụng.	\N	2025-05-05 05:00:21.417684	2025-05-05 05:00:21.417684	gcs
120	82a3a698-d886-4c7a-b18f-5295d6cf0346	82a3a698-d886-4c7a-b18f-5295d6cf0346.jpg	\N	Có một cái mô hình xe buýt xuất hiện ở trong bức ảnh.	\N	2025-05-07 12:44:46.285478	2025-05-07 12:44:46.285478	gcs
2	af341ed3-6215-4cce-ad27-deca8c7ada81	af341ed3-6215-4cce-ad27-deca8c7ada81.jpg	\N	Có một người phụ nữ đang đứng bên quầy hàng trái cây.	\N	2025-04-30 10:46:41.419976	2025-04-30 10:46:41.419976	gcs
100	b0f31524-4a5f-474f-83ce-2875a1411c0e	b0f31524-4a5f-474f-83ce-2875a1411c0e.jpg	\N	Có một người đang đứng ở bên một cái rổ đựng thức ăn.	\N	2025-05-04 20:43:51.703412	2025-05-04 20:43:51.703412	gcs
121	baabbb3c-d453-424b-9577-8581dbc4d9b5	baabbb3c-d453-424b-9577-8581dbc4d9b5.jpg	\N	Có một chiếc điện thoại đang được treo ở trên tường.	\N	2025-05-07 12:46:05.705264	2025-05-07 12:46:05.705264	gcs
4	ecea0490-42de-4d72-8fef-93748767bbdc	ecea0490-42de-4d72-8fef-93748767bbdc.jpg	\N	Có một người phụ nữ đang đứng bên quầy hàng trái cây.	\N	2025-04-30 10:54:19.931397	2025-04-30 10:54:19.931397	gcs
39	bf7aa9f9-0878-4e5c-969c-824e04304e3c	bf7aa9f9-0878-4e5c-969c-824e04304e3c.jpg	Khung cảnh nhìn từ trên cao của một cánh đồng	\N	3	2025-04-30 12:17:48.7595	2025-04-30 12:17:48.7595	gcs
168	edfef5d8-0346-4ac5-a4f4-f3b64e5f76ec	edfef5d8-0346-4ac5-a4f4-f3b64e5f76ec.jpg	\N	Có nhiều bức tranh được trưng bày ở trên tường.	\N	2025-05-12 16:49:30.866252	2025-05-12 16:49:30.866252	gcs
180	c74dde3d-2fd2-40d8-8478-47bf583287bf.jpg	c74dde3d-2fd2-40d8-8478-47bf583287bf.jpg	\N	Có nhiều con thuyền đang xuất hiện ở trên biển.	\N	2025-05-14 03:42:50.380353	2025-05-14 03:42:50.380353	gcs
110	0a540341-cea2-483d-bb3a-3ea3c7a6bd3a	0a540341-cea2-483d-bb3a-3ea3c7a6bd3a.jpg	\N	Ở trên mặt nước có sự xuất hiện của một vài con thuyền.	\N	2025-05-05 18:40:49.227989	2025-05-05 18:40:49.227989	gcs
169	35d23caf-c184-47e4-a30b-9a607f37c47f	35d23caf-c184-47e4-a30b-9a607f37c47f.jpg	\N	Có một chiếc ô tô màu trắng đang đỗ ở bên đường.	\N	2025-05-12 16:49:43.052492	2025-05-12 16:49:43.052492	gcs
103	56ab3337-d883-4aa5-879b-a71a7646ec6e	56ab3337-d883-4aa5-879b-a71a7646ec6e.jpg	Đây là bức tranh vẽ minh họa về một người đàn ông đeo kính	\N	36	2025-05-05 13:14:09.802319	2025-05-05 13:14:09.802319	gcs
159	a5ea9d65-d259-416e-b555-ec2e1277e67f	a5ea9d65-d259-416e-b555-ec2e1277e67f.jpg	Có một đoàn người đang tham gia rước kiệu ở lễ hội truyền thống	\N	1	2025-05-09 09:56:23.408487	2025-05-09 09:56:23.408487	gcs
147	ac6af231-e50c-44bd-b6d4-1f9b65ea2cf9	ac6af231-e50c-44bd-b6d4-1f9b65ea2cf9.jpg	\N	Có những chiếc đèn lồng được treo ở không gian phía trên của con phố.	\N	2025-05-09 09:49:00.512322	2025-05-09 09:49:00.512322	gcs
141	b5747962-4d87-46f1-b684-e491ce0b2c3d	b5747962-4d87-46f1-b684-e491ce0b2c3d.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một cái mô hình thuyền.	\N	2025-05-09 09:13:36.207995	2025-05-09 09:13:36.207995	gcs
178	df9a1a8c-d33c-4726-ba93-58e59ed01dd4	df9a1a8c-d33c-4726-ba93-58e59ed01dd4.jpg	a a a a a a a a 	\N	36	2025-05-13 13:50:25.138627	2025-05-13 13:50:25.138627	gcs
153	eceb76e3-3623-4a45-92a8-f61a8f8af683	eceb76e3-3623-4a45-92a8-f61a8f8af683.jpg	\N	Ở trên hồ sen có sự xuất hiện của một cậu bé đội nón lá.	\N	2025-05-09 09:50:52.105775	2025-05-09 09:50:52.105775	gcs
111	ee6f9d7d-59cc-4f05-a3d4-fa99847db8d0	ee6f9d7d-59cc-4f05-a3d4-fa99847db8d0.jpg	\N	Ở trong bức ảnh có sự xuất hiện của một cái cây cổ thụ.	\N	2025-05-07 11:52:10.798847	2025-05-07 11:52:10.798847	gcs
48	f858b8a9-8258-4d95-a04d-579d89a9d6af	f858b8a9-8258-4d95-a04d-579d89a9d6af.jpg	\N	Có một đĩa thức ăn xuất hiện ở trên tay của người đàn ông.	\N	2025-04-30 17:41:56.313764	2025-04-30 17:41:56.313764	gcs
181	75641388-d952-4bd8-9ca1-da6b7ce667bf.jpg	75641388-d952-4bd8-9ca1-da6b7ce667bf.jpg	t e e e e e e e e	\N	36	2025-05-14 03:42:54.15114	2025-05-14 03:42:54.15114	gcs
\.


--
-- Data for Name: model_versions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.model_versions (id, version_name, model_path, is_active, description, created_at) FROM stdin;
\.


--
-- Data for Name: user_activities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_activities (id, activity_type, user_id, ip_address, details, created_at) FROM stdin;
79	visit	1	127.0.0.1	{"path": "/api/admin/dashboard/top-contributors", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-05-01 19:29:05.013698
80	visit	1	127.0.0.1	{"path": "/api/admin/dashboard/top-contributors", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-05-01 19:29:33.347073
81	caption	\N	127.0.0.1	{"image_id": "3db14e35-4136-4a75-9976-33cf7ee4d6a7"}	2025-05-02 18:12:39.701585
82	caption	\N	127.0.0.1	{"image_id": "7d025169-bdeb-4b1a-956d-779f7d297d4c"}	2025-05-02 18:13:28.280217
44	caption	\N	127.0.0.1	{"image_id": "e8165b43-3e6a-4208-af76-235c87fdcb57"}	2025-04-30 12:18:47.482903
7	contribution	\N	127.0.0.1	{"image_id": "0bf13a87-de2e-4904-ad87-857396abc7be", "contribution_id": 1}	2025-04-30 11:15:06.146229
42	contribution	\N	127.0.0.1	{"image_id": "01ae1a59-4440-442b-939b-a8d95e5eec19", "contribution_id": 36}	2025-04-30 12:18:35.383758
43	contribution	\N	127.0.0.1	{"image_id": "ba1ae077-c3fd-4c62-a188-b354f2f31ac8", "contribution_id": 37}	2025-04-30 12:18:44.128182
45	contribution	\N	127.0.0.1	{"image_id": "20cd82ad-2cf6-4e42-af76-35aa77a718ff", "contribution_id": 38}	2025-04-30 12:18:55.623872
83	caption	\N	127.0.0.1	{"image_id": "ec9ceaa7-1617-4e68-ab7f-1c12ce70ea81"}	2025-05-02 18:18:59.827437
84	caption	\N	127.0.0.1	{"image_id": "fd39a0fe-3dd9-4aac-a2ad-8ba43ad12085"}	2025-05-02 18:20:28.010838
85	rating	1	127.0.0.1	{"rating": 1, "image_id": "fd39a0fe-3dd9-4aac-a2ad-8ba43ad12085"}	2025-05-02 18:20:33.490666
86	caption	\N	127.0.0.1	{"image_id": "c385eefe-d61b-4475-80d0-5428804d90fe"}	2025-05-04 11:00:46.777665
87	caption	\N	127.0.0.1	{"image_id": "42f94d8f-e342-44ce-9e10-b3cb70160191"}	2025-05-04 11:02:22.244324
88	caption	\N	127.0.0.1	{"image_id": "a38bf6d5-63ed-48ee-b073-9dfe2680889b"}	2025-05-04 12:13:58.47254
89	caption	\N	127.0.0.1	{"image_id": "a7abe65d-022b-4aa2-8b4a-d296507e58ed"}	2025-05-04 12:16:16.636907
90	caption	\N	127.0.0.1	{"image_id": "ebebc713-7129-44d0-bfdb-ed928939133e"}	2025-05-04 12:43:40.23723
91	caption	\N	127.0.0.1	{"image_id": "929618be-5a61-4818-bc65-998c541edb50"}	2025-05-04 13:16:00.078075
92	caption	\N	127.0.0.1	{"image_id": "53d583af-5731-4580-b61f-059e43917e50"}	2025-05-04 13:28:15.808436
93	caption	\N	127.0.0.1	{"image_id": "441165fb-029f-409b-9c1a-a4ebcfbeddbf"}	2025-05-04 13:55:59.295163
94	caption	\N	127.0.0.1	{"image_id": "026d0d33-c907-4505-8eef-72f36106034f"}	2025-05-04 14:09:00.136679
95	caption	\N	127.0.0.1	{"image_id": "b5b3849f-b56b-4c81-9f5e-340089e7b8b5"}	2025-05-04 14:11:13.670069
96	caption	\N	127.0.0.1	{"image_id": "eb9fc3ed-c439-46b5-acf7-2dfe32ae3fe1"}	2025-05-04 14:14:18.782057
97	caption	\N	127.0.0.1	{"image_id": "35bdba09-d1eb-4a79-beb9-1db2d03edf1c"}	2025-05-04 14:14:37.467279
99	visit	\N	127.0.0.1	{"path": "/", "referrer": null, "user_agent": "curl/8.13.0"}	2025-05-04 14:31:14.997627
100	caption	\N	127.0.0.1	{"image_id": "4935a7bb-26fc-4a91-ada2-ed5e425e25b7"}	2025-05-04 14:36:47.927875
101	visit	\N	127.0.0.1	{"path": "/", "referrer": null, "user_agent": "curl/8.13.0"}	2025-05-04 14:43:08.412047
102	caption	\N	127.0.0.1	{"image_id": "b3327abf-1072-4e96-93a2-f7f9b63ae37d"}	2025-05-04 14:47:27.295772
103	caption	\N	127.0.0.1	{"image_id": "9dc3e3a3-4409-491f-b6c0-5d1187d99158"}	2025-05-04 19:42:10.039547
104	rating	\N	127.0.0.1	{"rating": 5, "image_id": "9dc3e3a3-4409-491f-b6c0-5d1187d99158"}	2025-05-04 19:42:18.279293
105	contribution	36	127.0.0.1	{"image_id": "35d438ac-541f-4ee7-b3b3-026e518f89cb", "contribution_id": 42}	2025-05-04 19:44:28.594148
106	contribution	1	127.0.0.1	{"image_id": "c95894b4-5b5f-4a7a-a44b-d3903024ce45", "contribution_id": 43}	2025-05-04 19:44:54.2722
107	caption	\N	127.0.0.1	{"image_id": "924c0e05-4b4a-433f-9b50-a6e58e913875"}	2025-05-04 19:45:20.273595
108	contribution	36	127.0.0.1	{"image_id": "d113b7ca-2425-43d7-802f-d048ce4175f4", "contribution_id": 44}	2025-05-04 19:45:39.043614
109	contribution	1	127.0.0.1	{"image_id": "a44c6ae9-874e-46ac-b5ae-3c4635468401", "contribution_id": 45}	2025-05-04 19:47:27.108691
3	caption	\N	127.0.0.1	{"image_id": "6dbe2c7a-6f4f-4a25-95e8-d88aa8dad0ab"}	2025-04-30 10:49:20.536315
4	caption	\N	127.0.0.1	{"image_id": "ecea0490-42de-4d72-8fef-93748767bbdc"}	2025-04-30 10:54:19.948479
5	rating	\N	127.0.0.1	{"rating": 5, "image_id": "ecea0490-42de-4d72-8fef-93748767bbdc"}	2025-04-30 10:54:24.685957
6	rating	\N	127.0.0.1	{"rating": 5, "image_id": "ecea0490-42de-4d72-8fef-93748767bbdc"}	2025-04-30 10:54:28.544203
40	contribution	3	127.0.0.1	{"image_id": "a304da5d-bda4-413c-9ea4-ef48c72a44db", "contribution_id": 34}	2025-04-30 12:17:39.069656
41	contribution	3	127.0.0.1	{"image_id": "bf7aa9f9-0878-4e5c-969c-824e04304e3c", "contribution_id": 35}	2025-04-30 12:17:48.765647
46	contribution	1	127.0.0.1	{"image_id": "e25266ff-bdf2-4cb2-af1d-5bf8eb4dba04", "contribution_id": 39}	2025-04-30 12:26:44.55385
47	contribution	1	127.0.0.1	{"image_id": "862b023b-59de-43f7-84d7-68ff21251619", "contribution_id": 40}	2025-04-30 12:26:49.5297
48	visit	1	127.0.0.1	{"path": "/api/admin/contributions", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 12:36:35.510918
160	contribution	36	127.0.0.1	{"image_id": "60338027-6f7f-434d-ac68-0732f32cc728", "contribution_id": 56}	2025-05-08 10:28:29.395828
162	download_approved_data	1	\N	{"count": 12, "timestamp": "2025-05-08T22:09:29.847565"}	2025-05-08 22:09:29.851238
167	caption	\N	127.0.0.1	{"image_id": "e6aa7b82-a463-4ced-a8e2-e59e674e7b80"}	2025-05-09 08:51:20.612015
172	rating	36	127.0.0.1	{"rating": 5, "image_id": "05daa6d3-51c4-4c4f-9f09-b24e76be52da"}	2025-05-09 09:12:26.878421
177	caption	\N	127.0.0.1	{"image_id": "83b0e6da-6611-4477-8260-e6564af04946"}	2025-05-09 09:48:23.875812
182	rating	1	127.0.0.1	{"rating": 5, "image_id": "ac6af231-e50c-44bd-b6d4-1f9b65ea2cf9"}	2025-05-09 09:49:06.314095
187	caption	\N	127.0.0.1	{"image_id": "2906bc1e-91dd-44f7-a207-979fce13f4a9"}	2025-05-09 09:49:59.786127
192	rating	1	127.0.0.1	{"rating": 5, "image_id": "c2f38fc9-741e-47be-b0d3-a6a123caba32"}	2025-05-09 09:50:41.685508
197	contribution	1	127.0.0.1	{"image_id": "a69f7d66-5a99-429d-8f29-580866a632b6", "contribution_id": 60}	2025-05-09 09:54:16.983744
202	contribution	1	127.0.0.1	{"image_id": "f1506bfb-675c-4360-9cd3-128cbf9a396f", "contribution_id": 65}	2025-05-09 09:58:31.298944
205	caption	\N	127.0.0.1	{"image_id": "f52973bc-ed62-4b55-8547-6e09d462c1bd"}	2025-05-12 16:47:37.932581
210	caption	\N	127.0.0.1	{"image_id": "35d23caf-c184-47e4-a30b-9a607f37c47f"}	2025-05-12 16:49:43.060978
211	caption	\N	127.0.0.1	{"image_id": "c5e28d40-8968-4f3b-9cea-e2003ef1e8d2"}	2025-05-13 09:18:58.465168
216	caption	\N	127.0.0.1	{"image_id": "090efaad-4367-4ed7-9a63-60feff89aed6"}	2025-05-13 13:03:50.609002
221	caption	\N	127.0.0.1	{"image_id": "4d3e8545-b42d-4032-b570-302487fa1b1d"}	2025-05-13 13:49:44.061886
49	visit	1	127.0.0.1	{"path": "/api/admin/contributions", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 12:37:25.711814
50	visit	1	127.0.0.1	{"path": "/api/admin/contributions", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 12:37:57.384469
51	visit	1	127.0.0.1	{"path": "/api/admin/contributions", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 12:37:59.531318
52	visit	1	127.0.0.1	{"path": "/api/admin/contributions", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 12:38:03.928605
53	contribution	1	127.0.0.1	{"image_id": "5b8a4c93-e427-4ea2-af46-2d2a12d59a6e", "contribution_id": 41}	2025-04-30 16:16:02.6119
54	visit	3	127.0.0.1	{"path": "/api/user/profile", "referrer": "http://localhost:5173/profile", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 17:40:11.730741
55	caption	3	127.0.0.1	{"image_id": "f3660bfa-4eb5-4f7a-bdac-5e2dcc9b1966"}	2025-04-30 17:40:48.04129
56	visit	3	127.0.0.1	{"path": "/api/auth/me", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 17:41:45.122822
57	caption	\N	127.0.0.1	{"image_id": "f858b8a9-8258-4d95-a04d-579d89a9d6af"}	2025-04-30 17:41:56.3192
58	caption	\N	127.0.0.1	{"image_id": "ec6ffe7a-91de-4238-b7ae-dbd1d9faadd7"}	2025-04-30 17:42:13.781846
59	caption	3	127.0.0.1	{"image_id": "7b1928bc-f73d-4d09-be9e-ace243d6794b"}	2025-04-30 17:43:12.123232
60	caption	1	127.0.0.1	{"image_id": "4c9c8b1a-831f-42ae-86b7-188655e87392"}	2025-04-30 17:45:29.582913
61	visit	1	127.0.0.1	{"path": "/api/auth/me", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 17:45:56.934005
62	caption	\N	127.0.0.1	{"image_id": "ea07c7a0-1cf8-4ac7-81b8-a0f0c31b5fbd"}	2025-04-30 17:47:27.275143
63	caption	1	127.0.0.1	{"image_id": "be436a0e-dace-4187-8c25-cdf179978371"}	2025-04-30 17:48:41.010469
64	visit	1	127.0.0.1	{"path": "/api/auth/me", "referrer": "http://localhost:5173/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 17:57:46.171923
65	caption	\N	127.0.0.1	{"image_id": "15c0c241-15cc-4f7a-8140-2da386f9840d"}	2025-04-30 17:57:59.517399
66	caption	\N	127.0.0.1	{"image_id": "09915551-4274-4f1e-ae61-2ef29cc9ecf0"}	2025-04-30 17:58:30.532658
67	caption	\N	127.0.0.1	{"image_id": "8fef23e3-83fb-44c5-9a2b-9359b1b54f39"}	2025-04-30 17:59:06.598879
98	rating	\N	127.0.0.1	{"rating": 4, "image_id": "35bdba09-d1eb-4a79-beb9-1db2d03edf1c"}	2025-05-04 14:14:46.363754
161	contribution	36	127.0.0.1	{"image_id": "514398ff-71d3-46ba-81e0-c0be8c87aa90", "contribution_id": 57}	2025-05-08 10:37:35.497079
163	caption	\N	127.0.0.1	{"image_id": "cd634d5b-56d8-4407-9e3f-271a7f555a6d"}	2025-05-08 15:11:03.496671
168	caption	\N	127.0.0.1	{"image_id": "c231010e-65b2-43a4-96ed-4d0d728eb500"}	2025-05-09 09:02:53.175811
173	caption	\N	127.0.0.1	{"image_id": "b5747962-4d87-46f1-b684-e491ce0b2c3d"}	2025-05-09 09:13:36.216
178	rating	1	127.0.0.1	{"rating": 3, "image_id": "83b0e6da-6611-4477-8260-e6564af04946"}	2025-05-09 09:48:32.149531
183	caption	\N	127.0.0.1	{"image_id": "d8f07d3d-3f3f-46d1-9f89-21abdfa67159"}	2025-05-09 09:49:23.030338
188	rating	1	127.0.0.1	{"rating": 5, "image_id": "2906bc1e-91dd-44f7-a207-979fce13f4a9"}	2025-05-09 09:50:04.221552
193	caption	\N	127.0.0.1	{"image_id": "eceb76e3-3623-4a45-92a8-f61a8f8af683"}	2025-05-09 09:50:52.111511
198	contribution	1	127.0.0.1	{"image_id": "15e8e83d-093a-4bc7-bb4c-8e01099f0b55", "contribution_id": 61}	2025-05-09 09:54:50.853715
203	contribution	1	127.0.0.1	{"image_id": "b0bf8cff-62b9-4bb2-b36c-906b2280b21f", "contribution_id": 66}	2025-05-09 09:59:21.885788
206	caption	\N	127.0.0.1	{"image_id": "93d7cb36-c1f7-4612-b3b6-036e16b52c6e"}	2025-05-12 16:47:49.003656
212	caption	\N	127.0.0.1	{"image_id": "22d9aded-e03f-4e0e-98cd-85b260316a27"}	2025-05-13 09:19:30.9596
217	caption	\N	127.0.0.1	{"image_id": "def80f03-037a-438b-a66a-99da5c290343"}	2025-05-13 13:15:13.367893
222	caption	\N	127.0.0.1	{"image_id": "8d28dca7-b55d-49dc-a707-37fc0ffb4375"}	2025-05-13 13:50:03.882559
68	visit	3	127.0.0.1	{"path": "/api/user/profile", "referrer": "http://192.168.1.12:5173/profile", "user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"}	2025-04-30 17:59:44.526049
69	visit	3	127.0.0.1	{"path": "/api/user/profile", "referrer": "http://localhost:5173/profile", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-04-30 18:00:09.184837
70	caption	3	127.0.0.1	{"image_id": "bbeea78f-7229-4d8a-a53d-1bc1b94244b3"}	2025-05-01 17:21:24.163963
71	caption	3	127.0.0.1	{"image_id": "fca77d1d-670b-421d-8e35-31dc66800ad9"}	2025-05-01 17:23:06.310137
72	rating	3	127.0.0.1	{"rating": 4, "image_id": "fca77d1d-670b-421d-8e35-31dc66800ad9"}	2025-05-01 17:23:10.799285
73	caption	\N	127.0.0.1	{"image_id": "4275b703-4034-4383-9306-b629356f4115"}	2025-05-01 18:07:50.852054
74	rating	\N	127.0.0.1	{"rating": 4, "image_id": "4275b703-4034-4383-9306-b629356f4115"}	2025-05-01 18:08:06.141593
75	visit	\N	127.0.0.1	{"path": "/api/uploads/", "referrer": null, "user_agent": "curl/8.13.0"}	2025-05-01 18:23:51.606469
76	visit	\N	127.0.0.1	{"path": "/uploads/", "referrer": null, "user_agent": "curl/8.13.0"}	2025-05-01 18:23:59.707321
77	visit	\N	127.0.0.1	{"path": "/api", "referrer": null, "user_agent": "curl/8.13.0"}	2025-05-01 18:24:04.480321
78	caption	\N	127.0.0.1	{"image_id": "9a1d0c3c-2e99-47ed-bec6-850aee1c2caf"}	2025-05-01 18:25:46.600029
164	caption	\N	127.0.0.1	{"image_id": "a7b7bc5b-9ff4-4a29-8f0e-c2c222a434af"}	2025-05-08 15:11:20.585803
169	caption	\N	127.0.0.1	{"image_id": "ea82a8ba-89e4-4e58-86b8-21f17833d41b"}	2025-05-09 09:05:59.302074
174	caption	\N	127.0.0.1	{"image_id": "00330ac3-1531-4122-a23f-eadb377c2c09"}	2025-05-09 09:14:28.475026
179	caption	\N	127.0.0.1	{"image_id": "fe393289-3544-46d5-9071-a1410bf302fc"}	2025-05-09 09:48:43.114232
184	rating	1	127.0.0.1	{"rating": 5, "image_id": "d8f07d3d-3f3f-46d1-9f89-21abdfa67159"}	2025-05-09 09:49:26.932343
189	caption	\N	127.0.0.1	{"image_id": "46cbc9c6-50d9-4732-8703-08e8426c6a80"}	2025-05-09 09:50:21.856854
194	rating	1	127.0.0.1	{"rating": 2, "image_id": "eceb76e3-3623-4a45-92a8-f61a8f8af683"}	2025-05-09 09:51:00.333667
199	contribution	1	127.0.0.1	{"image_id": "d8df917a-f188-433e-84eb-518ad0284dce", "contribution_id": 62}	2025-05-09 09:55:35.70033
204	caption	\N	127.0.0.1	{"image_id": "c4129c3f-01c4-4028-b1a1-b3a6b288a1cf"}	2025-05-09 10:01:40.462999
207	caption	\N	127.0.0.1	{"image_id": "856d18f2-00fa-422c-8f13-45c3d02bce6b"}	2025-05-12 16:49:07.83537
213	visit	36	127.0.0.1	{"path": "/api/profile", "referrer": "https://vic.phambatrong.com/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-05-13 09:41:54.235911
218	rating	36	127.0.0.1	{"rating": 5, "image_id": "def80f03-037a-438b-a66a-99da5c290343"}	2025-05-13 13:15:15.723514
223	contribution	36	127.0.0.1	{"image_id": "df9a1a8c-d33c-4726-ba93-58e59ed01dd4", "contribution_id": 68}	2025-05-13 13:50:25.160953
165	caption	\N	127.0.0.1	{"image_id": "06667e1b-f40f-49b4-8c6b-fc8d9a401cba"}	2025-05-08 15:12:13.304524
170	caption	\N	127.0.0.1	{"image_id": "b46ccf97-34ae-464d-a99f-7fd5a3efa323"}	2025-05-09 09:08:53.68262
175	caption	\N	127.0.0.1	{"image_id": "561e5ee8-7f7c-4d4b-a65f-5a09aa3cd63d"}	2025-05-09 09:17:00.084332
180	rating	1	127.0.0.1	{"rating": 4, "image_id": "fe393289-3544-46d5-9071-a1410bf302fc"}	2025-05-09 09:48:47.428073
185	caption	\N	127.0.0.1	{"image_id": "42b9dd17-29d6-4d19-9562-4fb7b8731501"}	2025-05-09 09:49:39.734607
190	rating	1	127.0.0.1	{"rating": 4, "image_id": "46cbc9c6-50d9-4732-8703-08e8426c6a80"}	2025-05-09 09:50:26.78052
195	contribution	1	127.0.0.1	{"image_id": "1a0629b0-b2f6-471e-9a8a-2743b3821ae8", "contribution_id": 58}	2025-05-09 09:52:42.837533
200	contribution	1	127.0.0.1	{"image_id": "a5ea9d65-d259-416e-b555-ec2e1277e67f", "contribution_id": 63}	2025-05-09 09:56:23.418418
208	caption	\N	127.0.0.1	{"image_id": "a3221fd4-c52e-45f3-b2b8-a29c2875c5ae"}	2025-05-12 16:49:20.001896
110	contribution	1	127.0.0.1	{"image_id": "1e50f574-4f68-4088-be33-4458131de206", "contribution_id": 46}	2025-05-04 20:03:42.464177
111	contribution	1	127.0.0.1	{"image_id": "c9a375f3-9e63-43ea-9ed4-0f3a70c170e5", "contribution_id": 47}	2025-05-04 20:05:11.46408
112	contribution	1	127.0.0.1	{"image_id": "71573fdd-2f68-4b93-a147-cbb14e856e77", "contribution_id": 48}	2025-05-04 20:09:17.016004
113	caption	\N	127.0.0.1	{"image_id": "433d3af5-5e5a-4c3c-8a12-07339bcc1c44"}	2025-05-04 20:18:57.338834
114	caption	\N	127.0.0.1	{"image_id": "d7f9d43f-0577-48cd-97ea-ba3c1da68fe4"}	2025-05-04 20:20:35.154418
115	caption	\N	127.0.0.1	{"image_id": "beaadd09-095a-4f23-aedf-470895b3cb96"}	2025-05-04 20:20:52.321189
116	caption	\N	127.0.0.1	{"image_id": "e9c4062b-ddf9-41ee-b8ac-5d82eddb719b"}	2025-05-04 20:21:15.395273
117	caption	\N	127.0.0.1	{"image_id": "fa5435ec-e4db-4086-95f2-001d177c0242"}	2025-05-04 20:21:27.412093
118	caption	\N	127.0.0.1	{"image_id": "bca7a5fa-2394-44a6-a34a-81d5920e0137"}	2025-05-04 20:22:21.558104
119	caption	\N	127.0.0.1	{"image_id": "0b212e77-12b9-4c5c-85d1-2604bd7d40d7"}	2025-05-04 20:23:58.150611
120	caption	\N	127.0.0.1	{"image_id": "f3449afd-c47e-4a53-8a37-ca2ccb64e3d5"}	2025-05-04 20:26:15.984475
121	caption	\N	127.0.0.1	{"image_id": "3ac9fdfe-eeba-48b6-8cd7-308f4da93355"}	2025-05-04 20:26:18.884359
122	caption	\N	127.0.0.1	{"image_id": "c292680c-a3b5-410b-aa88-20be596b1965"}	2025-05-04 20:29:04.601279
123	caption	\N	127.0.0.1	{"image_id": "57224543-065a-4242-bb9c-5a002d77ea68"}	2025-05-04 20:29:18.514516
124	contribution	1	127.0.0.1	{"image_id": "daa9fc5f-e867-47c1-af6c-e0b3d75e0b35", "contribution_id": 49}	2025-05-04 20:43:43.542783
125	caption	\N	127.0.0.1	{"image_id": "b0f31524-4a5f-474f-83ce-2875a1411c0e"}	2025-05-04 20:43:51.711815
126	caption	\N	127.0.0.1	{"image_id": "54cf140e-6374-4d45-8cf0-5395231463cf"}	2025-05-05 04:58:43.782373
127	caption	\N	127.0.0.1	{"image_id": "a71135c5-9225-4d5a-aa98-429c666be28e"}	2025-05-05 05:00:21.425899
128	visit	1	127.0.0.1	{"path": "/api/admin/contributions/count", "referrer": "https://vic.phambatrong.com/", "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0"}	2025-05-05 06:12:38.698556
129	download_approved_data	1	\N	{"count": 10, "timestamp": "2025-05-06T10:17:57.362990"}	2025-05-05 13:17:57.366959
130	download_approved_data	1	\N	{"count": 10, "timestamp": "2025-05-06T10:20:31.958438"}	2025-05-05 13:20:31.962199
131	contribution	36	127.0.0.1	{"image_id": "56ab3337-d883-4aa5-879b-a71a7646ec6e", "contribution_id": 50}	2025-05-05 13:14:09.812958
132	contribution	36	127.0.0.1	{"image_id": "70a4273a-eef7-40e2-8a56-648187c5e90f", "contribution_id": 51}	2025-05-05 13:25:47.064021
1	caption	\N	127.0.0.1	{"image_id": "bd35730c-953a-4a8f-a235-a4ca826a445d"}	2025-04-30 10:42:30.31855
2	caption	\N	127.0.0.1	{"image_id": "af341ed3-6215-4cce-ad27-deca8c7ada81"}	2025-04-30 10:46:41.431633
214	download_approved_data	36	\N	{"count": 20, "timestamp": "2025-05-13T17:10:51.311180"}	2025-05-13 17:10:51.315278
219	caption	\N	127.0.0.1	{"image_id": "b3ba2c10-68bf-488b-9da2-e436b71c37f6"}	2025-05-13 13:29:57.979897
224	contribution	36	127.0.0.1	{"image_id": "f4ea2ed7-7e82-4d35-8c83-fc27cd66b718", "contribution_id": 69}	2025-05-13 13:50:49.987443
133	contribution	36	127.0.0.1	{"image_id": "2160ad04-251e-4262-9bf0-05adcdf34d30", "contribution_id": 52}	2025-05-05 13:37:45.630021
134	download_approved_data	1	\N	{"count": 11, "timestamp": "2025-05-06T17:50:35.466083"}	2025-05-05 20:50:35.470887
135	caption	\N	127.0.0.1	{"image_id": "0f12474a-b8ba-466a-8d23-42acab2d72f8"}	2025-05-05 14:13:36.223772
136	caption	\N	127.0.0.1	{"image_id": "8ef3fbde-57c8-4d65-a896-9fd776b32584"}	2025-05-05 14:14:21.487487
137	caption	\N	127.0.0.1	{"image_id": "3177c03a-da65-4530-ac88-1e4c08f0224d"}	2025-05-05 14:14:50.652866
138	contribution	1	127.0.0.1	{"image_id": "789c2945-b188-4e76-ab04-b985045ea25c", "contribution_id": 53}	2025-05-05 14:15:55.128753
139	caption	\N	127.0.0.1	{"image_id": "0a540341-cea2-483d-bb3a-3ea3c7a6bd3a"}	2025-05-05 18:40:49.23674
140	caption	\N	127.0.0.1	{"image_id": "ee6f9d7d-59cc-4f05-a3d4-fa99847db8d0"}	2025-05-07 11:52:10.811412
141	caption	\N	127.0.0.1	{"image_id": "4cf1b615-be92-4f2d-b01d-3fe6122fb2f6"}	2025-05-07 11:52:22.292353
142	caption	\N	127.0.0.1	{"image_id": "8f25d618-b40f-46cd-98dc-87be4f252b70"}	2025-05-07 11:52:31.636864
143	caption	\N	127.0.0.1	{"image_id": "6db76e18-6d8d-4c3c-b6a2-fa5a086e0955"}	2025-05-07 12:02:25.707251
144	caption	\N	127.0.0.1	{"image_id": "e546487d-7075-4c28-baa1-c8f8e91b12fc"}	2025-05-07 12:02:47.340246
145	caption	\N	127.0.0.1	{"image_id": "7e7b811f-79d7-4191-a2c4-285c8c350df3"}	2025-05-07 12:07:50.459659
146	caption	\N	127.0.0.1	{"image_id": "226851ab-3921-4bb9-bf51-c5ef6b5cb395"}	2025-05-07 12:08:49.208092
147	caption	\N	127.0.0.1	{"image_id": "55e1c32d-6876-4a53-8883-915512d39645"}	2025-05-07 12:11:13.654346
148	caption	\N	127.0.0.1	{"image_id": "6aea609f-4507-4e67-a4b9-494149cf4ad6"}	2025-05-07 12:11:43.160806
149	rating	36	127.0.0.1	{"rating": 5, "image_id": "6aea609f-4507-4e67-a4b9-494149cf4ad6"}	2025-05-07 12:11:55.296239
150	caption	\N	127.0.0.1	{"image_id": "82a3a698-d886-4c7a-b18f-5295d6cf0346"}	2025-05-07 12:44:46.2943
151	caption	\N	127.0.0.1	{"image_id": "baabbb3c-d453-424b-9577-8581dbc4d9b5"}	2025-05-07 12:46:05.714862
152	caption	\N	127.0.0.1	{"image_id": "08fd84ed-30a1-4558-8de9-62dfc99847b6"}	2025-05-07 12:46:24.733337
153	caption	\N	127.0.0.1	{"image_id": "58ad701c-0dc3-4f4d-a47e-f14aadcead93"}	2025-05-07 12:48:11.306577
154	contribution	36	127.0.0.1	{"image_id": "033f8caf-21b2-4064-8886-80b9d49db248", "contribution_id": 54}	2025-05-07 12:49:49.258766
155	contribution	36	127.0.0.1	{"image_id": "03056bdc-7681-49f0-ad1c-59676033d8e4", "contribution_id": 55}	2025-05-07 12:54:28.096875
156	caption	\N	127.0.0.1	{"image_id": "65e93a55-d4ee-40aa-8bc4-755ed6608691"}	2025-05-07 12:55:10.567059
157	caption	\N	127.0.0.1	{"image_id": "6c83b55d-752e-4f3b-9d45-7da8a8de9b52"}	2025-05-07 12:56:35.854867
158	caption	\N	127.0.0.1	{"image_id": "1def30bc-b2ed-476c-b9f7-c79df9a475a4"}	2025-05-07 13:00:59.015813
159	caption	\N	127.0.0.1	{"image_id": "0dffe044-e27e-48e7-b8ca-1fa9f6ba516b"}	2025-05-07 13:01:32.46425
166	caption	\N	127.0.0.1	{"image_id": "e40ae8e3-a88c-40eb-b46c-6d25e552005c"}	2025-05-08 15:12:13.635503
171	caption	\N	127.0.0.1	{"image_id": "05daa6d3-51c4-4c4f-9f09-b24e76be52da"}	2025-05-09 09:11:02.863217
176	caption	\N	127.0.0.1	{"image_id": "782cb38f-e0e5-4786-acd5-a4710cf53c7a"}	2025-05-09 09:17:48.395567
181	caption	\N	127.0.0.1	{"image_id": "ac6af231-e50c-44bd-b6d4-1f9b65ea2cf9"}	2025-05-09 09:49:00.521494
186	rating	1	127.0.0.1	{"rating": 5, "image_id": "42b9dd17-29d6-4d19-9562-4fb7b8731501"}	2025-05-09 09:49:46.768841
191	caption	\N	127.0.0.1	{"image_id": "c2f38fc9-741e-47be-b0d3-a6a123caba32"}	2025-05-09 09:50:37.065164
196	contribution	1	127.0.0.1	{"image_id": "f207eeba-3bf0-4ab6-b08d-a1754e540942", "contribution_id": 59}	2025-05-09 09:53:22.068303
201	contribution	1	127.0.0.1	{"image_id": "5a4c0812-333e-4e58-806f-b4c374df5644", "contribution_id": 64}	2025-05-09 09:57:03.420413
209	caption	\N	127.0.0.1	{"image_id": "edfef5d8-0346-4ac5-a4f4-f3b64e5f76ec"}	2025-05-12 16:49:30.874911
215	contribution	36	127.0.0.1	{"image_id": "a08744f3-b358-4d6e-8158-c46756640489", "contribution_id": 67}	2025-05-13 10:25:31.003814
220	download_approved_data	36	\N	{"count": 15, "timestamp": "2025-05-13T20:48:49.193532"}	2025-05-13 20:48:49.198032
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, email, password, full_name, biography, is_admin, created_at, updated_at, avatar, storage_type) FROM stdin;
1	admin	admin@example.com	$2b$12$lpAbfqinj0xcm9ldahAU.ecHMe8uYJY78F41U7OYvXm1mCK9fNjxG	Phạm Bá Trọng	\N	t	2025-04-30 08:25:49.334132	2025-05-12 08:30:54.782454	78a877b082cf4738bf64c04c80c26c04_34603ce8a80b1ce9a768cad7ebf63c56.jpg	gcs
38	test	a@gmail.com	$2b$12$djwSAtM6cwb5vIWh1p9jjeXyOYxnKgl9Q3Uix4TahCYg/w6dFOGPC	Phạm Văn A	\N	f	2025-05-13 10:07:31.062984	2025-05-13 10:09:28.630743	ae19d17382a74d7d9e1aba64e896344d_Screenshot_2025-05-01_at_21-31-11_Vietnamese_Image_Captioning.png	gcs
36	pat0nn	phambatrong.pbt@gmail.com	$2b$12$VFlqMaR9vm.9BSNqjte40e4MG8GoHHN7wDUV7R4d8OOFX2Kv4SbDy	Phạm Bá Trọng		t	2025-05-04 19:43:53.228611	2025-05-13 09:43:32.527732	be478e1da81943d9a80bc913974e8f3a_minimal_01.jpg	gcs
39	test2	b@gmail.com	$2b$12$NOtcP0ZlT97GHAAme64NS.X0s8CW3rzhm.AWMVcsxMtv8rftE/zc.	Phạm Văn D	\N	f	2025-05-13 10:10:14.113548	2025-05-13 10:10:14.113548	default.jpg	gcs
3	2	1@example.com	$2b$12$BhO8QmbvdJsyW5qE/paje.I8FbSK2ZZAcdsnO/eeLNJlrOJ3ZgBA.			f	2025-04-30 11:11:20.266883	2025-05-13 13:16:34.764258	default.jpg	gcs
\.


--
-- Name: caption_ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.caption_ratings_id_seq', 21, true);


--
-- Name: contributions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.contributions_id_seq', 67, true);


--
-- Name: daily_stats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.daily_stats_id_seq', 8, true);


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.images_id_seq', 181, true);


--
-- Name: model_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.model_versions_id_seq', 1, false);


--
-- Name: user_activities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_activities_id_seq', 213, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 36, true);


--
-- Name: caption_ratings caption_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.caption_ratings
    ADD CONSTRAINT caption_ratings_pkey PRIMARY KEY (id);


--
-- Name: contributions contributions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contributions
    ADD CONSTRAINT contributions_pkey PRIMARY KEY (id);


--
-- Name: daily_stats daily_stats_date_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats
    ADD CONSTRAINT daily_stats_date_key UNIQUE (date);


--
-- Name: daily_stats daily_stats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.daily_stats
    ADD CONSTRAINT daily_stats_pkey PRIMARY KEY (id);


--
-- Name: images images_image_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_image_id_key UNIQUE (image_id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: model_versions model_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_pkey PRIMARY KEY (id);


--
-- Name: user_activities user_activities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: caption_ratings caption_ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.caption_ratings
    ADD CONSTRAINT caption_ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: contributions contributions_reviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contributions
    ADD CONSTRAINT contributions_reviewer_id_fkey FOREIGN KEY (reviewer_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: contributions contributions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.contributions
    ADD CONSTRAINT contributions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: images images_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: user_activities user_activities_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_activities
    ADD CONSTRAINT user_activities_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

