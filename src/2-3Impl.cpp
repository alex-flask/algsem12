

namespace
{

bool isLeaf(Node* node)
{
    return node->children[0] == nullptr;
}
int getMax(Node* node)
{
    while (!isLeaf(node))
        node = node->children[node->count];

    return node->keys[node->count - 1];
}
void borrowFromLeft(Node* parent, int i)
{
    Node* node = parent->children[i];
    Node* left = parent->children[i - 1];


    node->keys[0] = parent->keys[i - 1];


    parent->keys[i - 1] = left->keys[left->count - 1];


    if (!isLeaf(left)) {
        node->children[1] = node->children[0];
        node->children[0] = left->children[left->count];

        left->children[left->count] = nullptr;
    }

    node->count++;
    left->count--;

    Node::borrows++;
}
void borrowFromRight(Node* parent, int i)
{
    Node* node = parent->children[i];
    Node* right = parent->children[i + 1];


    node->keys[0] = parent->keys[i];


    parent->keys[i] = right->keys[0];


    for (int j = 0; j < right->count - 1; j++)
        right->keys[j] = right->keys[j + 1];


    if (!isLeaf(right)) {
        node->children[1] = right->children[0];

        for (int j = 0; j < right->count; j++)
            right->children[j] = right->children[j + 1];

        right->children[right->count] = nullptr;
    }

    node->count++;
    right->count--;

    Node::borrows++;
}
void merge(Node* parent, int i)
{
    Node* left = parent->children[i];
    Node* right = parent->children[i + 1];

    int leftCount = left->count;


    left->keys[left->count++] = parent->keys[i];


    for (int j = 0; j < right->count; j++)
        left->keys[left->count++] = right->keys[j];


    if (!isLeaf(right)) {
        for (int j = 0; j <= right->count; j++)
            left->children[leftCount + 1 + j] = right->children[j];
    }


    for (int j = i; j < parent->count - 1; j++)
        parent->keys[j] = parent->keys[j + 1];


    for (int j = i + 1; j < parent->count; j++)
        parent->children[j] = parent->children[j + 1];

    parent->children[parent->count] = nullptr;
    parent->count--;

    Node::merges++;

    delete right;
}
void fixZero(Node* parent, int i)
{

    if (i > 0 && parent->children[i - 1]->count == 2) {
        borrowFromLeft(parent, i);
    }


    else if (i < parent->count &&
             parent->children[i + 1]->count == 2) {
        borrowFromRight(parent, i);
    }


    else if (i > 0) {
        merge(parent, i - 1);
    }


    else {
        merge(parent, i);
    }
}
void removeRecursive(Node* node, int key)
{
    if (node == nullptr)
        return;


    int i = 0;

    while (i < node->count && key > node->keys[i])
        i++;


    if (i < node->count && node->keys[i] == key) {

        if (isLeaf(node)) {

            for (int j = i; j < node->count - 1; j++)
                node->keys[j] = node->keys[j + 1];

            node->count--;
            return;
        }


        int predecessor = getMax(node->children[i]);

        node->keys[i] = predecessor;


        removeRecursive(node->children[i], predecessor);
    }


    else {
        if (isLeaf(node))
            return;

        removeRecursive(node->children[i], key);
    }


    if (node->children[i]->count == 0)
        fixZero(node, i);
}
struct Stats {
    int keys = 0;
    int nodes = 0;
    int twoNodes = 0;
    int threeNodes = 0;
    int leaves = 0;
    int height = 0;
};
void collectStats(Node* node, Stats& stats, int depth)
{
    if (node == nullptr)
        return;

    stats.nodes++;
    stats.keys += node->count;

    if (node->count == 1)
        stats.twoNodes++;
    else if (node->count == 2)
        stats.threeNodes++;

    if (depth > stats.height)
        stats.height = depth;

    if (isLeaf(node)) {
        stats.leaves++;
        return;
    }

    for (int i = 0; i <= node->count; i++)
        collectStats(node->children[i], stats, depth + 1);
}
}

//TODO: 
Node* insert(Node* root, int key);
Node* remove(Node* root, int key)
{
    if (root == nullptr)
        return nullptr;

    removeRecursive(root, key);


    if (root->count == 0) {
        Node* newRoot = root->children[0];

        delete root;

        return newRoot;
    }

    return root;
}
//TODO:
Node* find(Node* root, int key);
void printStats(Node* root)
{
    Stats stats;

    collectStats(root, stats, 0);

    std::cout << "Количество ключей: " << stats.keys << '\n';
    std::cout << "Количество вершин: " << stats.nodes << '\n';
    std::cout << "Количество 2-вершин: " << stats.twoNodes << '\n';
    std::cout << "Количество 3-вершин: " << stats.threeNodes << '\n';
    std::cout << "Количество листьев: " << stats.leaves << '\n';
    std::cout << "Высота дерева: " << stats.height << '\n';
    std::cout << "Количество разделений: " << Node::splits << '\n';
    std::cout << "Количество слияний: " << Node::merges << '\n';
    std::cout << "Количество заимствований: " << Node::borrows << '\n';
}
