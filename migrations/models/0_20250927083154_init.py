from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "permissions" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "resource" VARCHAR(5) NOT NULL,
    "action" VARCHAR(6) NOT NULL
);
COMMENT ON COLUMN "permissions"."resource" IS 'FILE: file\nUSER: user\nTRIAL: trial';
COMMENT ON COLUMN "permissions"."action" IS 'READ: read\nWRITE: write\nUPDATE: update\nDELETE: delete';
CREATE TABLE IF NOT EXISTS "permission_groups" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "first_name" VARCHAR(50),
    "last_name" VARCHAR(50),
    "email" VARCHAR(200) NOT NULL UNIQUE,
    "username" VARCHAR(200) UNIQUE,
    "app_name" VARCHAR(200) UNIQUE,
    "password" VARCHAR(200) NOT NULL,
    "is_verified" BOOL NOT NULL DEFAULT False,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "last_login" TIMESTAMPTZ,
    "ip_address" VARCHAR(45)
);
CREATE TABLE IF NOT EXISTS "files" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "name" VARCHAR(150) NOT NULL,
    "slug" VARCHAR(250) NOT NULL UNIQUE,
    "type" VARCHAR(8) NOT NULL,
    "extension" VARCHAR(10),
    "mime_type" VARCHAR(100),
    "url" VARCHAR(500) NOT NULL,
    "size" BIGINT NOT NULL,
    "width" INT,
    "height" INT,
    "duration" DOUBLE PRECISION,
    "is_public" BOOL NOT NULL DEFAULT True,
    "is_active" BOOL NOT NULL DEFAULT True,
    "user_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_files_slug_1c60f3" ON "files" ("slug");
COMMENT ON COLUMN "files"."type" IS 'IMAGE: image\nVIDEO: video\nDOCUMENT: document\nAUDIO: audio';
CREATE TABLE IF NOT EXISTS "usage" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ,
    "output" TEXT[],
    "cloth_image_id" UUID REFERENCES "files" ("id") ON DELETE CASCADE,
    "front_face_id" UUID REFERENCES "files" ("id") ON DELETE CASCADE,
    "l_side_image_id" UUID REFERENCES "files" ("id") ON DELETE CASCADE,
    "r_side_image_id" UUID REFERENCES "files" ("id") ON DELETE CASCADE,
    "user_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE,
    "user_3d_id" UUID REFERENCES "files" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "permission_group_permissions" (
    "permission_groups_id" UUID NOT NULL REFERENCES "permission_groups" ("id") ON DELETE CASCADE,
    "permission_id" UUID NOT NULL REFERENCES "permissions" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_permission__permiss_8863c5" ON "permission_group_permissions" ("permission_groups_id", "permission_id");
CREATE TABLE IF NOT EXISTS "users_permission_groups" (
    "users_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "permissiongroup_id" UUID NOT NULL REFERENCES "permission_groups" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_users_permi_users_i_9954a4" ON "users_permission_groups" ("users_id", "permissiongroup_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
