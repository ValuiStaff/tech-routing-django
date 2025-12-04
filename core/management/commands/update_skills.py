from django.core.management.base import BaseCommand
from core.models import Skill


class Command(BaseCommand):
    help = 'Update skills to match new service types: Personal care, Domestic Assistance, Community Access, Transport, Behaviour Support, Support Coordination, Therapy Access, Assistive Tech, Life Skills Training'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--deactivate-old',
            action='store_true',
            help='Deactivate old skills that are not in the new list',
        )
    
    def handle(self, *args, **options):
        # New skills list
        new_skills = [
            'Personal care',
            'Domestic Assistance',
            'Community Access',
            'Transport',
            'Behaviour Support',
            'Support Coordination',
            'Therapy Access',
            'Assistive Tech',
            'Life Skills Training',
        ]
        
        self.stdout.write('Updating skills...')
        
        # Create or update each new skill
        created_count = 0
        updated_count = 0
        for skill_name in new_skills:
            slug = skill_name.lower().replace(' ', '-')
            skill, created = Skill.objects.get_or_create(
                slug=slug,
                defaults={'name': skill_name, 'is_active': True}
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {skill_name}'))
            else:
                # Update name if it changed
                if skill.name != skill_name:
                    skill.name = skill_name
                    skill.is_active = True
                    skill.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'↻ Updated: {skill.name} → {skill_name}'))
                else:
                    skill.is_active = True
                    skill.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Already exists: {skill_name}'))
        
        # Optionally deactivate old skills
        if options['deactivate_old']:
            all_skills = Skill.objects.all()
            deactivated_count = 0
            for skill in all_skills:
                if skill.name not in new_skills:
                    skill.is_active = False
                    skill.save()
                    deactivated_count += 1
                    self.stdout.write(self.style.WARNING(f'✗ Deactivated: {skill.name}'))
            
            if deactivated_count > 0:
                self.stdout.write(self.style.WARNING(f'\nDeactivated {deactivated_count} old skills'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Done! Created: {created_count}, Updated: {updated_count}, Total active: {Skill.objects.filter(is_active=True).count()}'
        ))


