-- Digital Music Store - Sample Schema for Neon PostgreSQL
-- Compatible with Neon (https://neon.tech)
-- Generated from SDD Academy project data

BEGIN;

-- artists: Music artists
CREATE TABLE "artists" (
  "id" SERIAL PRIMARY KEY,
  "name" TEXT NOT NULL,
  "country" TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- INSERT sample data here based on your project requirements

-- albums: Albums by artists
CREATE TABLE "albums" (
  "id" SERIAL PRIMARY KEY,
  "artist_id" INTEGER NOT NULL,
  "title" TEXT NOT NULL,
  "release_year" INTEGER,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- INSERT sample data here based on your project requirements

-- songs: Individual songs
CREATE TABLE "songs" (
  "id" SERIAL PRIMARY KEY,
  "album_id" INTEGER NOT NULL,
  "title" TEXT NOT NULL,
  "duration_seconds" INTEGER,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- INSERT sample data here based on your project requirements

-- playlists: User-created playlists
CREATE TABLE "playlists" (
  "id" SERIAL PRIMARY KEY,
  "title" TEXT NOT NULL,
  "owner_user_id" INTEGER,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- INSERT sample data here based on your project requirements

-- reviews: User reviews and ratings
CREATE TABLE "reviews" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER,
  "song_id" INTEGER,
  "rating" SMALLINT,
  "body" TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- INSERT sample data here based on your project requirements

COMMIT;

-- Ready to use with Neon: https://neon.tech/docs/import/import-sample-data