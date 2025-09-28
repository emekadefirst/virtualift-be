from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usage" DROP CONSTRAINT IF EXISTS "fk_usage_files_b13f33b1";
        ALTER TABLE "usage" RENAME COLUMN "user_3d_id" TO "output_id";
        ALTER TABLE "usage" ADD "user_full_image_id" UUID;
        ALTER TABLE "usage" DROP COLUMN "output";
        ALTER TABLE "usage" ADD CONSTRAINT "fk_usage_files_647d726b" FOREIGN KEY ("output_id") REFERENCES "files" ("id") ON DELETE CASCADE;
        ALTER TABLE "usage" ADD CONSTRAINT "fk_usage_files_df318780" FOREIGN KEY ("user_full_image_id") REFERENCES "files" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "usage" DROP CONSTRAINT IF EXISTS "fk_usage_files_df318780";
        ALTER TABLE "usage" DROP CONSTRAINT IF EXISTS "fk_usage_files_647d726b";
        ALTER TABLE "usage" ADD "output" TEXT[];
        ALTER TABLE "usage" RENAME COLUMN "output_id" TO "user_3d_id";
        ALTER TABLE "usage" DROP COLUMN "user_full_image_id";
        ALTER TABLE "usage" ADD CONSTRAINT "fk_usage_files_b13f33b1" FOREIGN KEY ("user_3d_id") REFERENCES "files" ("id") ON DELETE CASCADE;"""
