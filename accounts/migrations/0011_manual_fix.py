from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_remove_historicalevents_upvotes_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE historicalevents DROP COLUMN IF EXISTS upvote_count;",
            "ALTER TABLE historicalevents ADD COLUMN upvote_count INTEGER DEFAULT 0;"
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS accounts_eventupvote;",
            "CREATE TABLE accounts_eventupvote (id INTEGER PRIMARY KEY);"
        ),
    ] 