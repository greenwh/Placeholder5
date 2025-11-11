"""
Vancian Magic System - AD&D 1e spell memorization and casting
"""

import random
from typing import Dict, List, Optional
from ..entities.player import PlayerCharacter, Spell
from ..entities.character import Character
from ..systems.saving_throws import SavingThrowResolver


class MagicSystem:
    """Handles spell memorization and casting"""

    def __init__(self):
        self.save_resolver = SavingThrowResolver()

    def cast_spell(self, caster: PlayerCharacter, spell_name: str,
                   targets: List[Character]) -> Dict:
        """
        Cast a memorized spell

        Args:
            caster: Character casting the spell
            spell_name: Name of the spell
            targets: List of potential targets

        Returns:
            Dict with: success, narrative, effect_results
        """

        # Check if spell is memorized and available
        spell = caster.use_spell_slot(spell_name)

        if not spell:
            return {
                'success': False,
                'narrative': f"You don't have {spell_name} memorized or it's already been cast!",
                'effect_results': {}
            }

        # Execute spell effect
        effect_results = self._execute_spell_effect(spell, caster, targets)

        return {
            'success': True,
            'narrative': f"You cast {spell.name}! {effect_results['narrative']}",
            'effect_results': effect_results
        }

    def _execute_spell_effect(self, spell: Spell, caster: PlayerCharacter,
                              targets: List[Character]) -> Dict:
        """
        Execute spell-specific logic

        Args:
            spell: The spell being cast
            caster: Character casting the spell
            targets: List of potential targets

        Returns:
            Dict with narrative and mechanical results
        """

        # Dispatch to spell-specific handlers
        spell_key = spell.name.lower().replace(' ', '_').replace('-', '_')

        handlers = {
            'sleep': self._spell_sleep,
            'magic_missile': self._spell_magic_missile,
            'cure_light_wounds': self._spell_cure_light_wounds,
            'protection_from_evil': self._spell_protection_from_evil,
            'detect_magic': self._spell_detect_magic,
            'burning_hands': self._spell_burning_hands,
            'charm_person': self._spell_charm_person
        }

        handler = handlers.get(spell_key)
        if handler:
            return handler(spell, caster, targets)
        else:
            return {
                'narrative': f"{spell.name} fizzles - effect not yet implemented.",
                'affected': []
            }

    def _spell_sleep(self, spell: Spell, caster: PlayerCharacter,
                     targets: List[Character]) -> Dict:
        """Sleep spell: affects 2d4 HD of creatures"""

        total_hd = random.randint(2, 8)  # 2d4

        # Sort targets by level/HD (lowest first)
        sorted_targets = sorted(targets, key=lambda t: t.level)

        affected = []
        hd_count = 0

        for target in sorted_targets:
            # Check immunity
            if hasattr(target, 'is_immune_to') and target.is_immune_to('sleep'):
                continue

            # Check if we have enough HD left
            if hd_count + target.level <= total_hd and target.is_alive:
                target.add_condition('sleeping')
                affected.append(target.name)
                hd_count += target.level

        if affected:
            narrative = f"The following creatures fall into a magical slumber: {', '.join(affected)}"
        else:
            narrative = "The spell fails to affect any creatures."

        return {
            'narrative': narrative,
            'affected': affected,
            'hd_affected': hd_count
        }

    def _spell_magic_missile(self, spell: Spell, caster: PlayerCharacter,
                            targets: List[Character]) -> Dict:
        """Magic Missile: 1d4+1 damage per missile, auto-hit"""

        # Number of missiles based on caster level
        num_missiles = 1 + (caster.level - 1) // 2
        num_missiles = min(5, num_missiles)  # Max 5 missiles

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target!",
                'affected': [],
                'total_damage': 0
            }

        target = targets[0]  # Magic missile targets one creature
        total_damage = 0

        for i in range(num_missiles):
            damage = random.randint(1, 4) + 1
            total_damage += damage

        target.take_damage(total_damage)

        narrative = f"{num_missiles} glowing missile{'s' if num_missiles > 1 else ''} "
        narrative += f"strike {target.name} for {total_damage} damage!"

        if not target.is_alive:
            narrative += f" {target.name} is slain!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'total_damage': total_damage
        }

    def _spell_cure_light_wounds(self, spell: Spell, caster: PlayerCharacter,
                                 targets: List[Character]) -> Dict:
        """Cure Light Wounds: heal 1d8 HP"""

        if not targets:
            return {
                'narrative': "No target to heal!",
                'affected': [],
                'healing': 0
            }

        target = targets[0]
        healing = random.randint(1, 8)

        old_hp = target.hp_current
        target.heal(healing)
        actual_healing = target.hp_current - old_hp

        narrative = f"{target.name} is healed for {actual_healing} HP!"

        return {
            'narrative': narrative,
            'affected': [target.name],
            'healing': actual_healing
        }

    def _spell_protection_from_evil(self, spell: Spell, caster: PlayerCharacter,
                                   targets: List[Character]) -> Dict:
        """Protection from Evil: +2 AC and saves vs evil"""

        if not targets:
            target = caster
        else:
            target = targets[0]

        target.add_condition('protected_from_evil')
        # In a full implementation, this would give +2 AC and save bonuses

        narrative = f"{target.name} is surrounded by a protective aura!"

        return {
            'narrative': narrative,
            'affected': [target.name]
        }

    def _spell_detect_magic(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Detect Magic: reveals magical auras"""

        # In the game context, this would check for magic items in room/inventory
        narrative = "Your eyes glow with eldritch sight. You can sense magical auras..."

        return {
            'narrative': narrative,
            'affected': [],
            'duration': 2 * caster.level  # rounds
        }

    def _spell_burning_hands(self, spell: Spell, caster: PlayerCharacter,
                            targets: List[Character]) -> Dict:
        """Burning Hands: cone of fire, 1d3+1 per level"""

        damage_per_target = caster.level + random.randint(1, 3)

        affected = []
        for target in targets:
            if target.is_alive:
                # Saving throw for half damage
                save_result = self.save_resolver.save_for_half_damage(
                    target, damage_per_target, 'spell'
                )
                affected.append(f"{target.name} ({save_result['final_damage']} dmg)")

        narrative = f"A cone of flame erupts from your hands! {', '.join(affected)}"

        return {
            'narrative': narrative,
            'affected': affected
        }

    def _spell_charm_person(self, spell: Spell, caster: PlayerCharacter,
                           targets: List[Character]) -> Dict:
        """Charm Person: make target friendly"""

        if not targets or not targets[0].is_alive:
            return {
                'narrative': "No valid target!",
                'affected': []
            }

        target = targets[0]

        # Check if target is person (humanoid)
        if target.size not in ['S', 'M']:
            return {
                'narrative': f"{target.name} is not a person - spell fails!",
                'affected': []
            }

        # Saving throw
        save_result = self.save_resolver.make_save(target, 'spell')

        if save_result['success']:
            narrative = f"{target.name} resists the charm!"
        else:
            target.add_condition('charmed')
            narrative = f"{target.name} is charmed! They see you as a trusted friend."

        return {
            'narrative': narrative,
            'affected': [target.name] if not save_result['success'] else []
        }
