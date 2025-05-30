import json
class g1:
    @staticmethod
    def process_response(raw) -> list:
        json_data = json.loads(raw)
        results = []
        print(raw)

        for news in json_data['items']:
            interrupter = news.get('aggregatedPosts')
            try:
                if interrupter:
                    for posts in news['aggregatedPosts']:
                        content = posts['content']
                        results.append((

                            content['title'].strip(),
                            content.get('summary', 'No Summary.'),
                            content['url'].strip()

                        ))

                else:
                    content = news['content']
                    results.append((
                        
                        content['title'].strip(),
                        content.get('summary', 'No Summary.'),
                        content['url'].strip()

                    ))
                    
            except KeyError:
                continue 
        return results