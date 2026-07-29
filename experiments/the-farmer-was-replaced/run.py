from cassandra.observation.engine import ObservationEngine


def main() -> None:
    engine = ObservationEngine()
    observation = engine.observe()
    print(observation)


if __name__ == "__main__":
    main()