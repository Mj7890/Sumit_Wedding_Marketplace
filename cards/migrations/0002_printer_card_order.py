from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrinterCardOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_type', models.CharField(choices=[('bride', 'लड़की का कार्ड (Bride)'), ('groom', 'लड़के का कार्ड (Groom)')], max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('printed', 'Printed'), ('delivered', 'Delivered')], default='pending', max_length=20)),
                ('primary_name', models.CharField(max_length=150, verbose_name='लड़की/लड़के का नाम')),
                ('primary_father_name', models.CharField(max_length=150, verbose_name='पिता का नाम')),
                ('primary_dada_name', models.CharField(blank=True, max_length=150, verbose_name='दादा का नाम')),
                ('primary_address', models.TextField(verbose_name='पता')),
                ('secondary_name', models.CharField(max_length=150, verbose_name='लड़के/लड़की का नाम')),
                ('secondary_father_name', models.CharField(max_length=150, verbose_name='पिता का नाम')),
                ('secondary_address', models.TextField(verbose_name='पता')),
                ('sagaai_date', models.CharField(blank=True, max_length=100, verbose_name='सगाई की तारीख')),
                ('sagaai_time', models.CharField(blank=True, max_length=50, verbose_name='सगाई का समय')),
                ('sagaai_preetibhoj', models.CharField(blank=True, max_length=100, verbose_name='सगाई प्रीतिभोज')),
                ('shaadi_date', models.CharField(blank=True, max_length=100, verbose_name='शादी की तारीख')),
                ('barat_swagat', models.CharField(blank=True, max_length=100, verbose_name='बारात स्वागत')),
                ('shaadi_preetibhoj', models.CharField(blank=True, max_length=100, verbose_name='शादी प्रीतिभोज')),
                ('vivah_sthal', models.TextField(blank=True, verbose_name='विवाह स्थल')),
                ('ghudchadi_time', models.CharField(blank=True, max_length=100, verbose_name='घुड़चढ़ी का समय')),
                ('barat_prasthan', models.CharField(blank=True, max_length=100, verbose_name='बारात प्रस्थान')),
                ('barat_destination', models.TextField(blank=True, verbose_name='बारात कहाँ जाएगी')),
                ('reception_date', models.CharField(blank=True, max_length=100, verbose_name='रिशेप्शन की तारीख')),
                ('reception_preetibhoj', models.CharField(blank=True, max_length=100, verbose_name='रिशेप्शन प्रीतिभोज')),
                ('reception_sthal', models.CharField(blank=True, max_length=150, verbose_name='रिशेप्शन स्थल')),
                ('extra_info', models.TextField(blank=True, verbose_name='अतिरिक्त जानकारी')),
                ('bal_aakanksha', models.CharField(blank=True, max_length=200, verbose_name='बाल आकांक्षा')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='फोन नं.')),
                ('darshanaabhilashi', models.CharField(blank=True, max_length=150, verbose_name='दर्शनाभिलाषी')),
                ('vineet', models.CharField(blank=True, max_length=150, verbose_name='विनीत')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='printer_orders', to='auth.user')),
            ],
            options={'ordering': ['-created_at'], 'verbose_name': 'Printer Card Order', 'verbose_name_plural': 'Printer Card Orders'},
        ),
    ]
