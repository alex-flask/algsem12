#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <vector>



struct Node {
    bool leaf;
    int n;
    int keys[2];
    Node* children[3];

    explicit Node(bool isLeaf) : leaf(isLeaf), n(0), keys{0, 0}, children{nullptr, nullptr, nullptr} {}
};

namespace {
long long splits = 0;
long long merges = 0;
long long redistributes = 0;
Node* statsRoot = nullptr;

struct InsertResult {
    bool inserted = false;
    bool split = false;
    int promoted = 0;
    Node* right = nullptr;
};

int childIndex(const Node* node, int key) {
    int i = 0;
    while (i < node->n && key > node->keys[i]) ++i;
    return i;
}

InsertResult insertRecursive(Node* node, int key) {
    if (node->leaf) {
        int i = 0;
        while (i < node->n && node->keys[i] < key) ++i;
        if (i < node->n && node->keys[i] == key) return {};

        if (node->n < 2) {
            for (int j = node->n; j > i; --j) node->keys[j] = node->keys[j - 1];
            node->keys[i] = key;
            ++node->n;
            return {true, false, 0, nullptr};
        }

        int values[3];
        for (int j = 0, old = 0; j < 3; ++j) {
            if (j == i) values[j] = key;
            else values[j] = node->keys[old++];
        }
        node->keys[0] = values[0];
        node->keys[1] = 0;
        node->n = 1;
        Node* right = new Node(true);
        right->keys[0] = values[2];
        right->n = 1;
        ++splits;
        return {true, true, values[1], right};
    }

    const int i = childIndex(node, key);
    if (i < node->n && node->keys[i] == key) return {};
    InsertResult childResult = insertRecursive(node->children[i], key);
    if (!childResult.inserted || !childResult.split) return childResult;

    int values[3];
    Node* kids[4];
    for (int j = 0; j < i; ++j) values[j] = node->keys[j];
    values[i] = childResult.promoted;
    for (int j = i; j < node->n; ++j) values[j + 1] = node->keys[j];
    for (int j = 0; j <= i; ++j) kids[j] = node->children[j];
    kids[i + 1] = childResult.right;
    for (int j = i + 1; j <= node->n; ++j) kids[j + 1] = node->children[j];

    if (node->n < 2) {
        const int newCount = node->n + 1;
        for (int j = 0; j < newCount; ++j) node->keys[j] = values[j];
        node->keys[newCount] = 0;
        for (int j = 0; j <= newCount; ++j) node->children[j] = kids[j];
        node->children[newCount + 1] = nullptr;
        node->n = newCount;
        return {true, false, 0, nullptr};
    }

    node->keys[0] = values[0];
    node->keys[1] = 0;
    node->n = 1;
    node->children[0] = kids[0];
    node->children[1] = kids[1];
    node->children[2] = nullptr;
    Node* right = new Node(false);
    right->keys[0] = values[2];
    right->n = 1;
    right->children[0] = kids[2];
    right->children[1] = kids[3];
    ++splits;
    return {true, true, values[1], right};
}

int predecessor(const Node* node) {
    while (!node->leaf) node = node->children[node->n];
    return node->keys[node->n - 1];
}

void removeParentEntry(Node* parent, int keyIndex, int childIndexToRemove) {
    for (int j = keyIndex; j < parent->n - 1; ++j) parent->keys[j] = parent->keys[j + 1];
    parent->keys[parent->n - 1] = 0;
    for (int j = childIndexToRemove; j < parent->n; ++j) parent->children[j] = parent->children[j + 1];
    parent->children[parent->n] = nullptr;
    --parent->n;
}



void fixUnderflow(Node* parent, int i) {
    Node* child = parent->children[i];

    if (i > 0 && parent->children[i - 1]->n == 2) {
        Node* left = parent->children[i - 1];
        child->keys[0] = parent->keys[i - 1];
        parent->keys[i - 1] = left->keys[left->n - 1];
        if (!child->leaf) {
            child->children[1] = child->children[0];
            child->children[0] = left->children[left->n];
            left->children[left->n] = nullptr;
        }
        left->keys[left->n - 1] = 0;
        --left->n;
        child->n = 1;
        ++redistributes;
        return;
    }

    if (i < parent->n && parent->children[i + 1]->n == 2) {
        Node* right = parent->children[i + 1];
        child->keys[0] = parent->keys[i];
        parent->keys[i] = right->keys[0];
        child->n = 1;
        if (!child->leaf) child->children[1] = right->children[0];
        right->keys[0] = right->keys[1];
        right->keys[1] = 0;
        if (!right->leaf) {
            right->children[0] = right->children[1];
            right->children[1] = right->children[2];
            right->children[2] = nullptr;
        }
        --right->n;
        ++redistributes;
        return;
    }

    if (i > 0) {
        Node* left = parent->children[i - 1];
        left->keys[left->n] = parent->keys[i - 1];
        if (!left->leaf) {
            left->children[left->n + 1] = child->children[0];
            child->children[0] = nullptr;
        }
        ++left->n;
        removeParentEntry(parent, i - 1, i);
        delete child;
    } else {
        Node* right = parent->children[1];
        child->keys[0] = parent->keys[0];
        child->keys[1] = right->keys[0];
        child->n = 2;
        if (!child->leaf) {
            child->children[1] = right->children[0];
            child->children[2] = right->children[1];
            right->children[0] = right->children[1] = nullptr;
        }
        removeParentEntry(parent, 0, 1);
        delete right;
    }
    ++merges;
}

bool removeRecursive(Node* node, int key) {
    int i = 0;
    while (i < node->n && key > node->keys[i]) ++i;

    if (i < node->n && node->keys[i] == key) {
        if (node->leaf) {
            for (int j = i; j < node->n - 1; ++j) node->keys[j] = node->keys[j + 1];
            node->keys[node->n - 1] = 0;
            --node->n;
            return true;
        }
        const int pred = predecessor(node->children[i]);
        node->keys[i] = pred;
        const bool removed = removeRecursive(node->children[i], pred);
        if (removed && node->children[i]->n == 0) fixUnderflow(node, i);
        return removed;
    }

    if (node->leaf) return false;
    const bool removed = removeRecursive(node->children[i], key);
    if (removed && node->children[i]->n == 0) fixUnderflow(node, i);
    return removed;
}

void destroy(Node* node) {
    if (!node) return;
    if (!node->leaf) for (int i = 0; i <= node->n; ++i) destroy(node->children[i]);
    delete node;
}

int height(const Node* node) {
    if (!node) return 0;
    int h = 1;
    while (!node->leaf) {
        ++h;
        node = node->children[0];
    }
    return h;
}

long long nodeCount(const Node* node) {
    if (!node) return 0;
    long long total = 1;
    if (!node->leaf) for (int i = 0; i <= node->n; ++i) total += nodeCount(node->children[i]);
    return total;
}

void collect(const Node* node, std::vector<int>& keys) {
    if (!node) return;
    if (node->leaf) {
        for (int i = 0; i < node->n; ++i) keys.push_back(node->keys[i]);
        return;
    }
    for (int i = 0; i < node->n; ++i) {
        collect(node->children[i], keys);
        keys.push_back(node->keys[i]);
    }
    collect(node->children[node->n], keys);
}

struct CheckResult {
    bool ok = true;
    int leafDepth = -1;
    long long keys = 0;
};

CheckResult checkNode(const Node* node, long long low, long long high, int depth) {
    if (!node || node->n < 1 || node->n > 2) return {false, -1, 0};
    for (int i = 0; i < node->n; ++i) {
        if (node->keys[i] <= low || node->keys[i] >= high) return {false, -1, 0};
        if (i && node->keys[i - 1] >= node->keys[i]) return {false, -1, 0};
    }
    if (node->leaf) return {true, depth, node->n};
    CheckResult result{true, -1, node->n};
    for (int i = 0; i <= node->n; ++i) {
        const long long childLow = i == 0 ? low : node->keys[i - 1];
        const long long childHigh = i == node->n ? high : node->keys[i];
        CheckResult child = checkNode(node->children[i], childLow, childHigh, depth + 1);
        if (!child.ok || (result.leafDepth != -1 && child.leafDepth != result.leafDepth)) result.ok = false;
        if (result.leafDepth == -1) result.leafDepth = child.leafDepth;
        result.keys += child.keys;
    }
    return result;
}
}

Node* find(Node* root, int key) {
    Node* current = root;
    while (current) {
        int i = 0;
        while (i < current->n && key > current->keys[i]) ++i;
        if (i < current->n && current->keys[i] == key) return current;
        if (current->leaf) return nullptr;
        current = current->children[i];
    }
    return nullptr;
}

Node* insert(Node* root, int key) {
    if (!root) {
        root = new Node(true);
        root->keys[0] = key;
        root->n = 1;
        statsRoot = root;
        return root;
    }
    InsertResult result = insertRecursive(root, key);
    if (result.split) {
        Node* newRoot = new Node(false);
        newRoot->keys[0] = result.promoted;
        newRoot->n = 1;
        newRoot->children[0] = root;
        newRoot->children[1] = result.right;
        root = newRoot;
    }
    statsRoot = root;
    return root;
}

Node* remove(Node* root, int key) {
    if (!root || !removeRecursive(root, key)) {
        statsRoot = root;
        return root;
    }
    if (root->n == 0) {
        Node* oldRoot = root;
        if (root->leaf) root = nullptr;
        else {
            root = root->children[0];
            oldRoot->children[0] = nullptr;
        }
        delete oldRoot;
    }
    statsRoot = root;
    return root;
}

void resetStats() { splits = merges = redistributes = 0; }

void printStats(const Node* root) {
    std::cout << "height=" << height(root)
              << " nodes=" << nodeCount(root)
              << " splits=" << splits
              << " merges=" << merges
              << " redistributes=" << redistributes << '\n';
}



void printStats() { printStats(statsRoot); }

namespace {
using Clock = std::chrono::steady_clock;
double elapsedMs(Clock::time_point start, Clock::time_point end) {
    return std::chrono::duration<double, std::milli>(end - start).count();
}

double median(std::vector<double> values) {
    std::sort(values.begin(), values.end());
    return values[values.size() / 2];
}

std::vector<int> randomSet() {
    std::srand(1);
    std::vector<int> values(10000);
    for (int& value : values) value = std::rand() % 100000;
    return values;
}

std::vector<int> sortedSet() {
    std::vector<int> values(10000);
    for (int i = 0; i < 10000; ++i) values[i] = i + 1;
    return values;
}

std::vector<int> hotspotSet() {
    std::srand(1);
    std::vector<int> values(10000, 42);
    for (int i = 5000; i < 10000; ++i) values[i] = std::rand() % 100000;
    return values;
}

void benchmark(const std::string& name, const std::vector<int>& data, bool csv) {
    std::set<int> unique(data.begin(), data.end());
    std::vector<double> insertTimes, searchTimes, removeTimes;
    int treeHeight = 0;
    long long nodeCountAfterInsert = 0, splitCount = 0, mergeCount = 0, redistributeCount = 0;

    for (int repetition = 0; repetition < 7; ++repetition) {
        Node* root = nullptr;
        resetStats();
        auto start = Clock::now();
        for (int key : data) root = insert(root, key);
        auto end = Clock::now();
        insertTimes.push_back(elapsedMs(start, end));

        if (repetition == 0) {
            treeHeight = height(root);
            nodeCountAfterInsert = nodeCount(root);
            splitCount = splits;
        }

        start = Clock::now();
        for (int key : data) assert(find(root, key) != nullptr);
        end = Clock::now();
        searchTimes.push_back(elapsedMs(start, end));

        start = Clock::now();
        for (int key : data) root = remove(root, key);
        end = Clock::now();
        removeTimes.push_back(elapsedMs(start, end));
        if (repetition == 0) {
            mergeCount = merges;
            redistributeCount = redistributes;
        }
        assert(root == nullptr);
    }

    if (csv) {
        std::cout << name << ',' << data.size() << ',' << unique.size() << ',' << treeHeight << ','
                  << nodeCountAfterInsert << ',' << splitCount << ',' << mergeCount << ','
                  << redistributeCount << ',' << std::fixed << std::setprecision(3)
                  << median(insertTimes) << ',' << median(searchTimes) << ',' << median(removeTimes) << '\n';
    } else {
        std::cout << "\n" << name << " (N=" << data.size() << ", unique=" << unique.size() << ")\n"
                  << "insert_ms=" << std::fixed << std::setprecision(3) << median(insertTimes)
                  << " search_ms=" << median(searchTimes) << " remove_ms=" << median(removeTimes) << '\n'
                  << "height_after_insert=" << treeHeight << " nodes_after_insert=" << nodeCountAfterInsert
                  << " splits=" << splitCount << " merges=" << mergeCount
                  << " redistributes=" << redistributeCount << '\n';
    }
}

void selfTest() {
    std::mt19937 generator(2026);
    std::uniform_int_distribution<int> keyDistribution(-1000, 1000);
    std::bernoulli_distribution insertOperation(0.54);
    std::set<int> reference;
    Node* root = nullptr;
    resetStats();

    for (int step = 0; step < 30000; ++step) {
        const int key = keyDistribution(generator);
        if (insertOperation(generator)) {
            root = insert(root, key);
            reference.insert(key);
        } else {
            root = remove(root, key);
            reference.erase(key);
        }

        for (int probe = -1000; probe <= 1000; probe += 79)
            assert((find(root, probe) != nullptr) == (reference.count(probe) != 0));
        CheckResult check;
        if (root) check = checkNode(root, -2147483649LL, 2147483648LL, 1);
        else check = {true, -1, 0};
        assert(check.ok);
        assert(check.keys == static_cast<long long>(reference.size()));
        std::vector<int> actual;
        collect(root, actual);
        assert(std::vector<int>(reference.begin(), reference.end()) == actual);
    }
    destroy(root);
    std::cout << "Self-test passed: 30000 random insert/remove operations; invariants and std::set agree.\n";
}
}

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        selfTest();
        return 0;
    }
    const bool csv = argc == 2 && std::string(argv[1]) == "--csv";
    if (argc > 2 || (argc == 2 && !csv)) {
        std::cerr << "Usage: " << argv[0] << " [--self-test | --csv]\n";
        return 2;
    }

    if (csv) {
        std::cout << "dataset,input_count,unique_count,height,nodes,splits,merges,redistributes,insert_ms,search_ms,remove_ms\n";
    } else {
        std::cout << "Команда 1 — классическое 2-3 дерево; наборы семинара 11, 10000 операций.\n"
                  << "Random/Hotspot: rand() % 100000, seed=1; дубликаты игнорируются.\n";
    }
    benchmark("Random", randomSet(), csv);
    benchmark("Sorted", sortedSet(), csv);
    benchmark("Hotspot", hotspotSet(), csv);
}
