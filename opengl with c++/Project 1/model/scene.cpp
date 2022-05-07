#include "scene.h"

Scene::Scene() {

	PlayerCreateInfo playerInfo;
	playerInfo.eulers = { 0.0f, 0.0f,0.0f };
	playerInfo.position = { 0.0f, 0.0f, 1.0f };
	player = new Player(&playerInfo);
	enemySpawnRate = 0.02f;
	enemyShootRate = 0.02f;
	powerUpSpawnRate = 0.01;
}

void Scene::reset() {

	delete player;
	PlayerCreateInfo playerInfo;
	playerInfo.eulers = { 0.0f, 0.0f,0.0f };
	playerInfo.position = { 0.0f, 0.0f, 1.0f };
	player = new Player(&playerInfo);

	for (int i = 0; i < bullets.size(); ++i) {
		delete bullets[i];
	}
	bullets.clear();

	for (int i = 0; i < enemies.size(); ++i) {
		delete enemies[i];
	}
	enemies.clear();

	for (int i = 0; i < powerUps.size(); ++i) {
		delete powerUps[i];
	}
	powerUps.clear();
}

Scene::~Scene() {
	delete player;
}

void Scene::update(float rate) {

	unsigned seed = std::chrono::steady_clock::now().time_since_epoch().count();
	std::default_random_engine generator(seed);

	player->update(rate);
	if (player->position.z < -7) {
		reset();
	}

	std::vector<int> bin;
	for (int i = 0; i < bullets.size(); ++i) {
		SimpleComponent* bullet = bullets[i];
		bullet->update(rate);
		bool hitSomething = false;
		if ((bullet->position.x > 48) || (bullet->position.x < -10)) {
			bin.push_back(i);
			hitSomething = true;
		}
		if (player->state == STATE::STABLE) {
			if ((bullet->position.x > player->position.x - 2)
				&& (bullet->position.x < player->position.x + 2)
				&& (bullet->position.y > player->position.y - 2)
				&& (bullet->position.y < player->position.y + 2)
				&& !hitSomething) {
				player->health -= 1;
				bin.push_back(i);
				hitSomething = true;
			}
		}

		for (Enemy* enemy : enemies) {
			if (enemy->state == STATE::STABLE) {
				if ((bullet->position.x > enemy->position.x - 2)
					&& (bullet->position.x < enemy->position.x + 2)
					&& (bullet->position.y > enemy->position.y - 2)
					&& (bullet->position.y < enemy->position.y + 2)
					&& !hitSomething) {
					enemy->health -= 1;
					bin.push_back(i);
					hitSomething = true;
				}
			}
		}
	}

	for (int i = 0; i < bin.size(); ++i) {
		for (int j = i + 1; j < bin.size(); ++j) {
			if (bin[j] == bin[i]) {
				std::vector<int>::iterator iterator = bin.begin();
				std::advance(iterator, i);
				bin.erase(iterator);
			}
			else if (bin[j] > bin[i]) {
				bin[j] -= 1;
			}
		}
		delete bullets[i];
		std::vector<SimpleComponent*>::iterator iterator = bullets.begin();
		std::advance(iterator, i);
		bullets.erase(iterator);
	}
	bin.clear();
	
	float chance = generator() / 1e9;
	if ((chance < enemySpawnRate) && (enemies.size() < 12)) {
		EnemyCreateInfo createInfo;
		float x = std::min(36.0f, std::max(18.0f,static_cast<float>(6.0f * ((2.0f * (generator() / 2e9)) - 1.0f) + 24.0f)));
		float y = std::min(6.0f, std::max(-6.0f, static_cast<float>(6.0f * ((2.0f * (generator() / 2e9)) - 1.0f))));
		createInfo.position = glm::vec3(x, y, 8.0f);
		createInfo.eulers = glm::vec3(0.0f, 0.0f, 0.0f);
		Enemy* newEnemy = new Enemy(&createInfo);
		enemies.push_back(newEnemy);
	}
	for (int i = 0; i < enemies.size(); ++i) {
		Enemy* enemy = enemies[i];
		enemy->update(rate);
		if ((generator() / 1e9) < enemyShootRate) {
			shootEnemy(enemy);
		}
		if (enemy->position.z < -7) {
			bin.push_back(i);
		}
	}

	for (int i = 0; i < bin.size(); ++i) {
		for (int j = i + 1; j < bin.size(); ++j) {
			if (bin[j] == bin[i]) {
				std::vector<int>::iterator iterator = bin.begin();
				std::advance(iterator, i);
				bin.erase(iterator);
			}
			else if (bin[j] > bin[i]) {
				bin[j] -= 1;
			}
		}
		delete enemies[i];
		std::vector<Enemy*>::iterator iterator = enemies.begin();
		std::advance(iterator, i);
		enemies.erase(iterator);
	}
	bin.clear();

	chance = generator() / 1e9;
	if ((chance < powerUpSpawnRate) && (powerUps.size() < 6)) {
		ComponentCreateInfo createInfo;
		float x = std::min(36.0f, std::max(18.0f, static_cast<float>(6.0f * ((2.0f * (generator() / 2e9)) - 1.0f) + 24.0f)));
		float y = std::min(6.0f, std::max(-6.0f, static_cast<float>(6.0f * ((2.0f * (generator() / 2e9)) - 1.0f))));
		createInfo.position = glm::vec3(x, y, 1.0f);
		createInfo.velocity = glm::vec3(-0.5f, 0.0f, 0.0f);
		powerUps.push_back(new SimpleComponent(&createInfo));
	}
	for (int i = 0; i < powerUps.size(); ++i) {
		SimpleComponent* powerUp = powerUps[i];
		powerUp->update(rate);

		bool hitSomething = false;
		if ((powerUp->position.x > 48) || (powerUp->position.x < -10)) {
			bin.push_back(i);
			hitSomething = true;
		}
		if (player->state == STATE::STABLE) {
			if ((powerUp->position.x > player->position.x - 2)
				&& (powerUp->position.x < player->position.x + 2)
				&& (powerUp->position.y > player->position.y - 2)
				&& (powerUp->position.y < player->position.y + 2)
				&& !hitSomething) {
				player->health += 6;
				if (player->health > 18) {
					player->health = 18;
				}
				bin.push_back(i);
				hitSomething = true;
			}
		}
	}

	for (int i = 0; i < bin.size(); ++i) {
		for (int j = i + 1; j < bin.size(); ++j) {
			if (bin[j] == bin[i]) {
				std::vector<int>::iterator iterator = bin.begin();
				std::advance(iterator, i);
				bin.erase(iterator);
			}
			else if (bin[j] > bin[i]) {
				bin[j] -= 1;
			}
		}
		delete powerUps[i];
		std::vector<SimpleComponent*>::iterator iterator = powerUps.begin();
		std::advance(iterator, i);
		powerUps.erase(iterator);
	}
	bin.clear();
}

void Scene::movePlayer(glm::vec3 dPos) {
	player->velocity = dPos;
}

void Scene::shootPlayer() {
	if ((player->canShoot) && (player->state == STATE::STABLE)) {
		player->canShoot = false;
		player->reloadTime = 24.0f;
		ComponentCreateInfo createInfo;
		createInfo.position = player->position + glm::vec3(2.0f, 0.0f, 0.0f);
		createInfo.velocity = glm::vec3(2.0f, 0.0f, 0.0f);
		bullets.push_back(new SimpleComponent(&createInfo));
	}
}

void Scene::shootEnemy(Enemy* enemy) {
	if ((enemy->canShoot) && (enemy->state == STATE::STABLE)) {
		enemy->canShoot = false;
		enemy->reloadTime = 24.0f;
		ComponentCreateInfo createInfo;
		createInfo.position = enemy->position + glm::vec3(-2.0f, 0.0f, 0.0f);
		createInfo.velocity = glm::vec3(-2.0f, 0.0f, 0.0f);
		bullets.push_back(new SimpleComponent(&createInfo));
	}
}