struct Node {
    int keys[3];
    Node *children[4] = {};
    int count = 0;
    //MARK: Коля, это нужно будет обновлять при добавлении
    inline static long long splits = 0;
    inline static long long merges = 0;
    inline static long long borrows = 0;
};

Node* insert(Node* root, int key);
Node* remove(Node* root, int key);
Node* find(Node* root, int key);
void printStats(Node *root);
