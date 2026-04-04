class RuleEngine:
    @staticmethod
    def check_eligibility(profile: dict, benefit_criteria: dict) -> bool:
        """
        Runs simple rules. Custom parsing mapped from JSON.
        E.g. {"has_children": true, "max_child_age": 1}
        """
        # Children check
        if benefit_criteria.get("has_children"):
            family = profile.get("family", [])
            children = [f for f in family if f.get("relation") == "child"]
            if not children:
                return False
            max_age = benefit_criteria.get("max_child_age")
            if max_age:
                if not any(c.get("age", 99) <= max_age for c in children):
                    return False
        
        # Income check
        max_income = benefit_criteria.get("max_income")
        if max_income:
            if profile.get("income_monthly", 9999999) > max_income:
                return False

        # Add more mappings as rules expand
        return True
