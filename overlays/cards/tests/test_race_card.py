from unittest import TestCase
from unittest.mock import patch
from overlays.cards import RaceCard
from datetime import datetime


class RaceCardTestCase(TestCase):
    @patch('data.journal.JournalWatcher')
    @patch('pygame.surface.Surface')
    @patch('pygame.font.Font')
    @patch('data.config.Config')
    def test_fighter_test(self, journal_class, surface_class, font_class, config_class):
        journal = journal_class()
        surface = surface_class()
        config = config_class()
        surface.get_size.return_value = (100, 100)

        config.get_race.return_value = {
            "name": "Sample Race",
            "waypoints": [
                {"event": "LaunchFighter", "lat": 0, "lng": 0, "range": 0.1},
                {"event": "Pass", "lat": 0, "lng": 1, "range": 0.1},
                {"event": "DockFighter", "lat": 0, "lng": 0, "range": 0.1},
            ]
        }

        journal.get_race.return_value = config.get_race()
        card = RaceCard(surface, journal)

        time_start = datetime(year=2020, month=1, day=1, hour=1, minute=0, second=0)
        time_w1 = datetime(year=2020, month=1, day=1, hour=1, minute=0, second=30)
        time_end = datetime(year=2020, month=1, day=1, hour=1, minute=1, second=0)

        self.assertEqual(None, card.waypoints[0])
        self.assertEqual(None, card.waypoints[1])
        self.assertEqual(None, card.waypoints[2])

        # start
        journal.events = [
            {
                "timestamp": time_start,
                'event': 'LaunchFighter',
            }
        ]
        journal.get_status.return_value = {"Latitude": 0, "Longitude": 0}
        journal.now.return_value = time_start
        card.render()
        self.assertEqual(time_start, card.waypoints[0])
        self.assertEqual(None, card.waypoints[1])
        self.assertEqual(None, card.waypoints[2])

        # pass WP
        journal.get_status.return_value = {"timestamp": time_w1, "Latitude": 0, "Longitude": 1}
        journal.now.return_value = time_w1
        card.render()
        self.assertEqual(time_start, card.waypoints[0])
        self.assertEqual(time_w1, card.waypoints[1])
        self.assertEqual(None, card.waypoints[2])

        # to ignore
        journal.get_status.return_value = {"timestamp": time_w1, "Latitude": 0, "Longitude": -0.1}
        journal.now.return_value = time_w1
        card.render()
        self.assertEqual(time_start, card.waypoints[0])
        self.assertEqual(time_w1, card.waypoints[1])
        self.assertEqual(None, card.waypoints[2])

        # end race
        journal.events = [
            {
                "timestamp": time_end,
                'event': 'DockFighter',
            }
        ]
        journal.get_status.return_value = {"Latitude": 0, "Longitude": 0}
        journal.now.return_value = time_end
        card.render()
        self.assertEqual(time_start, card.waypoints[0])
        self.assertEqual(time_w1, card.waypoints[1])
        self.assertEqual(time_end, card.waypoints[2])