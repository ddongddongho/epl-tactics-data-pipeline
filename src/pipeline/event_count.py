from mrjob.job import MRJob
from mrjob.step import MRStep

class EventCount(MRJob):
    def steps(self):
        return [
            MRStep(mapper=self.mapper_get_events,
                   reducer=self.reducer_count_events)
        ]

    def mapper_get_events(self, _, line):
        data = line.split('\t')
        if len(data) == 3:
            team, event_type, time = data
            yield event_type, 1

    def reducer_count_events(self, event_type, counts):
        yield event_type, sum(counts)

if __name__ == '__main__':
    EventCount.run()
