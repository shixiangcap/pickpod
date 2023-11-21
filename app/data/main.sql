PRAGMA foreign_keys = false;

-- ----------------------------
-- Table structure for audio
-- ----------------------------
DROP TABLE IF EXISTS "audio";
CREATE TABLE "audio" (
  "id" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM PRIMARY KEY AUTOINCREMENT,
  "uuid" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "title" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "ext" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "web" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "url" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "duration" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "language" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "description" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "keyword" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "path" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "origin" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "status" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 1 COLLATE RTRIM,
  "createTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "updateTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM
);

-- ----------------------------
-- Table structure for formation
-- ----------------------------
DROP TABLE IF EXISTS "formation";
CREATE TABLE "formation" (
  "id" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM PRIMARY KEY AUTOINCREMENT,
  "uuid" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "audioId" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "content" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "mark" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "target" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "status" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 1 COLLATE RTRIM,
  "createTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "updateTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM
);

-- ----------------------------
-- Table structure for sentence
-- ----------------------------
DROP TABLE IF EXISTS "sentence";
CREATE TABLE "sentence" (
  "id" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM PRIMARY KEY AUTOINCREMENT,
  "uuid" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "audioId" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "content" text NOT NULL ON CONFLICT ROLLBACK DEFAULT '' COLLATE RTRIM,
  "start" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "end" real NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "speaker" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "status" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 1 COLLATE RTRIM,
  "createTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM,
  "updateTime" integer NOT NULL ON CONFLICT ROLLBACK DEFAULT 0 COLLATE RTRIM
);

-- ----------------------------
-- Auto increment value for audio
-- ----------------------------
UPDATE "main"."sqlite_sequence" SET seq = 0 WHERE name = 'audio';

-- ----------------------------
-- Auto increment value for formation
-- ----------------------------
UPDATE "main"."sqlite_sequence" SET seq = 0 WHERE name = 'formation';

-- ----------------------------
-- Auto increment value for sentence
-- ----------------------------
UPDATE "main"."sqlite_sequence" SET seq = 0 WHERE name = 'sentence';

PRAGMA foreign_keys = true;
