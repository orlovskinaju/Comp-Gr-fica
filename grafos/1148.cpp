#include <iostream>
#include <vector>
#include <queue>
#include <limits>
using namespace std;

const int INF = 1e9;

int dijkstra(int n, int origem, int destino, const vector<vector<pair<int, int>>>& grafo) {
    vector<int> dist(n + 1, INF);
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;

    dist[origem] = 0;
    pq.push({0, origem});

    while (!pq.empty()) {
        int d = pq.top().first;
        int u = pq.top().second;
        pq.pop();

        if (d > dist[u]) continue;

        for (auto [v, w] : grafo[u]) {
            if (dist[v] > dist[u] + w) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist[destino];
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    while (true) {
        int n, e;
        cin >> n >> e;
        if (n == 0 && e == 0) break;

        vector<vector<pair<int, int>>> grafo(n + 1);

        for (int i = 0; i < e; i++) {
            int x, y, h;
            cin >> x >> y >> h;
            bool tem_retorno = false;
            for (auto [viz, custo] : grafo[y]) {
                if (viz == x) {
                    tem_retorno = true;
                    break;
                }
            }
            if (tem_retorno) {
                grafo[x].push_back({y, 0});
                grafo[y].push_back({x, 0});
            } else {
                grafo[x].push_back({y, h});
            }
        }

        int k;
        cin >> k;

        for (int i = 0; i < k; i++) {
            int o, d;
            cin >> o >> d;
            int resp = dijkstra(n, o, d, grafo);
            if (resp == INF)
                cout << "Nao e possivel entregar a carta\n";
            else
                cout << resp << "\n";
        }

        cout << "\n"; 
    }

    return 0;
}
