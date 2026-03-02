from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ResultInstance",
        ),
        migrations.RemoveField(
            model_name="resultrecord",
            name="nand",
        ),
        migrations.RemoveField(
            model_name="resultrecord",
            name="nand_instance",
        ),
        migrations.RemoveField(
            model_name="resultrecord",
            name="nand_perf",
        ),
        migrations.RemoveField(
            model_name="resultrecord",
            name="cpu",
        ),
        migrations.RemoveField(
            model_name="resultrecord",
            name="dram",
        ),
        migrations.AddField(
            model_name="resultrecord",
            name="data",
            field=models.JSONField(
                blank=True,
                default=None,
                help_text="Free-form snapshot of hardware/config at record time",
                null=True,
            ),
        ),
    ]
