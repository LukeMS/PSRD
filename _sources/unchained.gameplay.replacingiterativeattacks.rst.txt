
.. _`unchained.gameplay.replacingiterativeattacks`:

.. contents:: \ 

.. _`unchained.gameplay.replacingiterativeattacks#removing_iterative_attacks`:

Removing Iterative Attacks
###########################

Iterative attacks allow combatants to deal a high amount of damage, but they can also make turns take a long time. Since a character's subsequent attacks have a bonus that's so much lower, this can lead to a lot of time spent on missed attacks. With this new system, an entire full attack resolves with a single d20 roll. Other sorts of attacks (such as attack actions, attacks of opportunity, and attacks granted by the Whirlwind Attack feat) are resolved as normal.

.. _`unchained.gameplay.replacingiterativeattacks#attack_results`:

.. list-table:: Attack Results
   :header-rows: 1
   :class: contrast-reading-table
   :widths: auto

   * - Attack Roll Result
     - Type of Hit
     - Damage Dealt
   * - Below AC by 6 or more
     - Miss
     - None
   * - Below AC by 5 or less
     - Glancing blow
     - 1/2 minimum damage
   * - Equal or exceed AC
     - Hit
     - Normal damage
   * - Exceed AC by 5 or more \*
     - Additional hit
     - Normal damage

.. _`unchained.gameplay.replacingiterativeattacks#maximum_hits`:

.. list-table:: Maximum Hits
   :header-rows: 1
   :class: contrast-reading-table
   :widths: auto

   * - Base Attack Bonus
     - Maximum Hits
   * - +0 to +5
     - 1
   * - +6 to +10
     - 2
   * - +11 to +15
     - 3
   * - +16 to +20
     - 4
   * - +21 to +25 \*
     - 5
   * - +26 to +30 \*
     - 6

**Notes:**

* Typically, only monsters have a base attack bonus this high.

.. _`unchained.gameplay.replacingiterativeattacks#the_basics`:

The Basics
***********

When making a full attack, roll only one attack roll and compare your result to the target's AC. If your attack result is lower than the target's AC by 6 or more, you miss and deal no damage. If your result is lower than the target's AC by 5 or less, you deliver a glancing blow, dealing an amount of damage equal to 1/2 the minimum damage you would normally deal on a hit with the weapon you're using. Effects that trigger on a hit do not trigger on a glancing blow. If your attack result equals or exceeds the target's AC, you score a hit, plus one additional hit for every 5 by which your roll exceeds that target's AC, up to your maximum number of hits. At first level, you can score a maximum of only one hit, but at base attack bonus +6 and at every +5 to your base attack bonus thereafter, you can score another. This is shown on :ref:`Table: Maximum Hits <unchained.gameplay.replacingiterativeattacks#maximum_hits>`\ , and also matches the progression of iterative attacks you'd gain if you were using the core rules for attacks. For each hit you score, roll damage separately; damage reduction applies to each hit. 

For example, say you have a base attack bonus of +8, are using a melee weapon that deals 1d10 points of damage on a hit, and have a Strength modifier of +4. Your target has an AC of 21. If your attack roll result is 15 or lower, you miss. If your result is 16–20, you deal a glancing blow for 2 points of damage (your damage die's minimum of 1 plus your Strength modifier of +4, divided by 2 and rounded down). If your result is 21–25, you hit and deal 1d10+4 points of damage. If your result is 26 or higher, you hit twice and deal 1d10+4 points of damage twice. Even if your result were 31 or higher, you would still hit only twice because your base attack bonus is lower than +11.

\ **Tracking**\ : When using this system, it speeds up the game if players calculate in advance the amount of damage they deal on a glancing blow with each weapon their characters use and write it on the character sheets. It also helps if the GM notes the monster's AC – 6, AC + 5, AC + 10, and AC + 15.

.. _`unchained.gameplay.replacingiterativeattacks#attacking_multiple_targets`:

Attacking Multiple Targets
===========================

If you have more than one maximum hit, you can declare you're making a full attack against more than one target. In that case, your number of hits is determined by the highest AC among your targets, and you can allocate your hits however you like among all the targets after determining your total number of hits—you can even choose not to hit the target whose AC you rolled against. This doesn't allow you to bypass effects that would prevent you from hitting a creature normally. For instance, you couldn't assign a hit to a creature under a \ *sanctuary*\  effect when making an attack roll against a different creature (unless you first succeeded on the required Will save).

.. _`unchained.gameplay.replacingiterativeattacks#critical_hits`:

Critical Hits
==============

When you threaten a critical hit, roll to confirm at your full bonus and apply the effects of the critical hit to any one of your hits. If your original attack roll scored multiple hits and the critical confirmation roll also falls within your weapon's critical threat range, you score two critical hits and can apply them to any two hits.

.. _`unchained.gameplay.replacingiterativeattacks#two_weapon_fighting`:

Two-Weapon Fighting
********************

When fighting with two weapons, use the lower attack bonus of the two weapons. If you score one hit, you also score a hit with your off-hand weapon. If you have Improved Two-Weapon Fighting and score two hits, you also score a second hit with your off-hand weapon, for a total of four. If you have Greater Two-Weapon Fighting and score three hits, you also score a third hit with your off-hand weapon, for a total of six.

\ **Critical Hits with Two-Weapon Fighting**\ : If you threaten a critical hit when using :ref:`Two-Weapon Fighting <corerulebook.feats#two_weapon_fighting>`\ , roll a single confirmation roll using the lower attack bonus among the two weapons. If you confirm, you score one critical hit with each weapon, so long as the initial roll threatened a critical with both weapons. For example, if you're fighting with a rapier and a light pick, roll an 18 on your initial attack roll, and confirm the critical hit, you score a critical hit with only the rapier. However, if you roll a 20 and confirm, you score a critical hit with each weapon.

.. _`unchained.gameplay.replacingiterativeattacks#natural_attacks`:

Natural Attacks
****************

If a creature with at least three natural attacks makes a full attack using only natural weapons, the creature has a maximum number of hits equal to the number of secondary attacks plus 1/2 the number of primary attacks (rounded up). The creature uses the lowest attack bonus of its primary natural weapons for its attack roll. For each hit it scores, the creature can choose to deal damage with any two primary natural weapons or any one secondary natural weapon. If it misses by 5 or less, it hits with one primary natural weapon instead of dealing a glancing blow. 

For example, a monster with two primary claw attacks and a secondary tail slap can score up to two hits. If it scores one hit, it can apply both of its claws or its tail slap. If it misses by 5 or less, it can apply one of its claws. If it succeeds by 5 or more, scoring two hits, it can apply all three of its attacks.

.. _`unchained.gameplay.replacingiterativeattacks#special_cases`:

Special Cases
**************

Dealing with spells and abilities that grant additional attacks, rerolls, or high bonuses can be tricky under this system. So many rules are based around iterative attacks that it's not possible to cover every type of effect that needs to be adjusted. GMs should use the following rules as guidelines when interpreting how to implement similar spells and abilities.

.. _`unchained.gameplay.replacingiterativeattacks#extra_attacks`:

Extra Attacks
==============

Effects such as \ *haste*\  that grant additional attacks instead raise your maximum number of hits by one. This includes secondary natural attacks made at the end of a manufactured weapon full attack.

.. _`unchained.gameplay.replacingiterativeattacks#rerolls`:

Rerolls
========

Since the full attack roll simulates a series of rolls, effects that grant or force single rerolls instead grant either a +2 bonus (if the attacker keeps the better roll, or the character causing the reroll intends to aid the attacker) or –2 penalty (if the attacker keeps the lower roll, or the character causing the reroll intends to hinder the attacker). Effects that would grant rerolls for allattack rolls made as part of the full attack allow the attacker to reroll the attack roll instead of imposing a bonus or penalty.

.. _`unchained.gameplay.replacingiterativeattacks#true_strike`:

True Strike
============

When using :ref:`true strike <corerulebook.spells.truestrike#true_strike>`\ with a full attack, first see how many hits you would have scored without :ref:`true strike <corerulebook.spells.truestrike#true_strike>`\ . A single casting of :ref:`true strike <corerulebook.spells.truestrike#true_strike>`\  adds at most one more hit.

.. _`unchained.gameplay.replacingiterativeattacks#variant_mobile_melee`: `unchained.gameplay.replacingiterativeattacks#variant:_mobile_melee`_

.. _`unchained.gameplay.replacingiterativeattacks#variant:_mobile_melee`:

Variant: Mobile Melee
**********************

This variant modification to removing iterative attacks allows a character greater mobility during a melee full attack rather than forcing them to stay put. When a character declares a melee full attack, she can also declare she will move before or after the attacks, up to a maximum of her movement speed. For every 5 feet she moves beyond the first 5 feet, she takes a –5 penalty on her attack roll for the purposes of determining extra hits only. Apply this penalty after determining whether she hits at least once.

The character can attempt an :ref:`Acrobatics <corerulebook.skills.acrobatics#acrobatics>`\  check to reduce this penalty by an amount equal to the result of her :ref:`Acrobatics <corerulebook.skills.acrobatics#acrobatics>`\  check divided by 5. No matter how high her :ref:`Acrobatics <corerulebook.skills.acrobatics#acrobatics>`\  check result may be, she can't reduce the penalty below –2 per 5 feet moved beyond the first 5 feet.

Characters with the :ref:`Spring Attack <corerulebook.feats#spring_attack>`\  feat can move before, after, and in between the attacks when using this option, and they reduce the penalty to –4 for every 5 feet moved beyond the first 5 feet.

