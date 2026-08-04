"""Registry for configuring Cassandra evaluation rules."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from cassandra.evaluation.rule import EvaluationRule


class RuleRegistry:
    """Maintain an ordered collection of uniquely named evaluation rules."""

    def __init__(
        self,
        rules: Iterable[EvaluationRule] | None = None,
    ) -> None:
        self._rules: dict[str, EvaluationRule] = {}

        for rule in rules or ():
            self.register(rule)

    def register(self, rule: EvaluationRule) -> None:
        """Register a rule under its stable identifier."""

        if rule.name in self._rules:
            raise ValueError(
                f"Evaluation rule is already registered: {rule.name}"
            )

        self._rules[rule.name] = rule

    def unregister(self, name: str) -> EvaluationRule:
        """Remove and return a registered rule."""

        try:
            return self._rules.pop(name)
        except KeyError as exc:
            raise KeyError(
                f"Evaluation rule is not registered: {name}"
            ) from exc

    def get(self, name: str) -> EvaluationRule:
        """Return a registered rule by name."""

        try:
            return self._rules[name]
        except KeyError as exc:
            raise KeyError(
                f"Evaluation rule is not registered: {name}"
            ) from exc

    def rules(self) -> tuple[EvaluationRule, ...]:
        """Return registered rules in registration order."""

        return tuple(self._rules.values())

    def names(self) -> tuple[str, ...]:
        """Return registered rule identifiers."""

        return tuple(self._rules)

    def __contains__(self, name: object) -> bool:
        return name in self._rules

    def __iter__(self) -> Iterator[EvaluationRule]:
        return iter(self._rules.values())

    def __len__(self) -> int:
        return len(self._rules)