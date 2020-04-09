import datetime
import faker
import json
import pathlib
import random

FAKE = faker.Faker()


class Users():
    def __init__(self, n_users, date):
        users = []
        for user_id in random.sample(range(3000), n_users):
            users.append({
                'update_time': date.isoformat() + 'T' + FAKE.time(),
                'user_id': user_id,
                'email': FAKE.safe_email(),
                'name': FAKE.name(),
                'environment': random.choice(['production', 'stage']),
            })
        self._randomly_duplicate(users)
        self.users = {date: users}

    @staticmethod
    def _randomly_duplicate(users):
        n_dup = round(len(users) * random.random() * 0.15 + 1)
        for _ in range(n_dup):
            users.append(random.choice(users))

    def update_users(self, n_update, date):
        day0 = min(self.users.keys())
        updated_users = []
        for _ in range(n_update):
            user = random.choice(self.users[day0]).copy()
            user['update_time'] = date.isoformat() + 'T' + FAKE.time(),
            user['email'] = FAKE.safe_email()
            updated_users.append(user)
        self._randomly_duplicate(updated_users)
        self.users[date] = updated_users

    def write_users(self, date):
        dest = pathlib.Path.cwd() / 'downloads/UserUpdates'
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f'{date.isoformat()}.log'
        with open(path, 'w') as f:
            for user in self.users[date]:
                line = [f'"{user[key]}"' for key in user]
                f.write(','.join(line))
                f.write('\n')


class PageViews():
    def __init__(self, users, *, n_pages=1000):
        self.users = users
        self.urls = [f'/product/{page_id}/' for page_id in range(n_pages)]
        self.page_views = {}

    def daily_views(self, date, *, n_views=500):
        todays_page_views = []
        for _ in range(n_views):
            user = random.choice(self.users)
            todays_page_views.append({
                'ts': date.isoformat() + 'T' + FAKE.time(),
                'url': random.choice(self.urls),
                'environment': user['environment'],
                'user_id': user['user_id']
            })
        self.page_views[date] = todays_page_views

    def write_page_views(self, date):
        dest = pathlib.Path.cwd() / 'downloads/PageViews'
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / f'{date.isoformat()}.log'
        with open(path, 'w') as f:
            for page_view in self.page_views[date]:
                json.dump(page_view, f)
                f.write('\n')


if __name__ == '__main__':
    n_days = 30
    n_users = 500
    day0 = datetime.date.today() - datetime.timedelta(days=n_days)
    users = Users(n_users, day0)
    for i in range(n_days):
        date = day0 + datetime.timedelta(days=i)
        p_update = random.random() * 0.9 + 0.1  # at least 10% update
        n_update = round(n_users * p_update)
        users.update_users(n_update, date)

    page_views = PageViews(users.users[day0])
    for date in users.users:
        users.write_users(date)
        page_views.daily_views(date, n_views=random.randint(100, 1000))
        page_views.write_page_views(date)
