import django.db.models.deletion
from django.db import migrations, models


def migrate_property_set_to_memberships(apps, schema_editor):
    """
    For each ExtendedProperty with property_set set, create a membership row.
    """
    ExtendedProperty = apps.get_model("properties", "ExtendedProperty")
    ExtendedPropertySetMembership = apps.get_model(
        "properties", "ExtendedPropertySetMembership"
    )
    for ep in ExtendedProperty.objects.filter(property_set__isnull=False):
        ExtendedPropertySetMembership.objects.create(
            property_set=ep.property_set,
            extended_property=ep,
            index=0,
        )


def delete_invalid_properties(apps, schema_editor):
    """
    Delete ExtendedProperty rows where content_type is NULL.
    These become invalid after content_type is made non-nullable.
    """
    ExtendedProperty = apps.get_model("properties", "ExtendedProperty")
    ExtendedProperty.objects.filter(content_type__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("properties", "0002_extendedproperty_default_value"),
    ]

    operations = [
        # 1. Create the new membership table
        migrations.CreateModel(
            name="ExtendedPropertySetMembership",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "index",
                    models.PositiveIntegerField(
                        help_text="Display order of this property within the set"
                    ),
                ),
                (
                    "extended_property",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to="properties.extendedproperty",
                    ),
                ),
                (
                    "property_set",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="memberships",
                        to="properties.extendedpropertyset",
                    ),
                ),
            ],
            options={
                "ordering": ["index"],
            },
        ),
        migrations.AddConstraint(
            model_name="extendedpropertysetmembership",
            constraint=models.UniqueConstraint(
                fields=("property_set", "extended_property"),
                name="unique_extended_prop_in_set",
            ),
        ),
        migrations.AddConstraint(
            model_name="extendedpropertysetmembership",
            constraint=models.UniqueConstraint(
                fields=("property_set", "index"),
                name="unique_index_in_extended_set",
            ),
        ),
        # 2. Data migration: copy property_set FK → membership rows
        migrations.RunPython(
            migrate_property_set_to_memberships,
            migrations.RunPython.noop,
        ),
        # 3. Cleanup: delete rows that will be invalid after content_type becomes required
        migrations.RunPython(
            delete_invalid_properties,
            migrations.RunPython.noop,
        ),
        # 4. Remove old constraints (must happen before removing fields/altering)
        migrations.RemoveConstraint(
            model_name="extendedproperty",
            name="extended_prop_single_binding",
        ),
        migrations.RemoveConstraint(
            model_name="extendedproperty",
            name="unique_extended_prop_per_set",
        ),
        # 6. Remove old unique_extended_prop_per_model_type (conditional) before re-adding unconditional
        migrations.RemoveConstraint(
            model_name="extendedproperty",
            name="unique_extended_prop_per_model_type",
        ),
        # 7. Remove property_set FK column
        migrations.RemoveField(
            model_name="extendedproperty",
            name="property_set",
        ),
        # 8. Make content_type non-nullable
        migrations.AlterField(
            model_name="extendedproperty",
            name="content_type",
            field=models.ForeignKey(
                help_text="Model type this property is bound to (e.g. Nand, Cpu, ResultWorkload).",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="extended_properties",
                to="contenttypes.contenttype",
            ),
        ),
        # 9. Add unconditional unique constraint (safe now that old one is removed)
        migrations.AddConstraint(
            model_name="extendedproperty",
            constraint=models.UniqueConstraint(
                fields=("content_type", "name"),
                name="unique_extended_prop_per_model_type",
            ),
        ),
    ]
